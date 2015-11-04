#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
import datetime
import shutil
from db_manager import *
from DragDropList import *
from Popups import *
from ReplayInfoFrame import *
from ReplayList import *
from ReplayEditFrame import *
import threading
import rl_paths
import replay_parser


class ReplayManager(tk.Frame):
    def __init__(self,parent, **kw):
        rl_paths.make_dirs()
        tk.Frame.__init__(self, parent, **kw)
        n = ttk.Notebook(self)
        f1 = tk.Frame(n)   # first page, which would get widgets gridded into it
        f2 = tk.Frame(n)   # second page
        n.add(f1, text='browse',sticky="nswe")
        n.add(f2, text='add',sticky="nswe")
        n.pack(fill="both",expand=1)
        self.start_browse_mode(f1)
        self.start_add_mode(f2)



    def start_browse_mode(self,frame):
        print "starting browse mode"
        tk.Label(frame,text="Replays").grid(row=0,column=0,sticky="NS")
        tk.Button(frame,text="Filter", command=self.filter_replays).grid(row=2,column=0,sticky="WE")
        tk.Label(frame,text="Staged").grid(row=0,column=2,sticky="NS")
        tk.Button(frame,text="Unstage",command=self.unstage_all).grid(row=2,column=2,sticky="WE")
        
        f  = tk.Frame(frame)
        f2 = tk.Frame(frame)
        scrollbar = tk.Scrollbar(f, orient=tk.VERTICAL)
        self.tracked_replays = ReplayList(f,yscrollcommand=scrollbar.set)
        self.tracked_replays.bind("<MouseWheel>",lambda event : self.tracked_replays.yview("scroll",-event.delta/120,"units"))
        scrollbar.config(command=self.tracked_replays.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tracked_replays.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.fetch_replays()

        
        scrollbar2 = tk.Scrollbar(f2, orient=tk.VERTICAL)
        self.staged_list = ReplayList(f2,yscrollcommand=scrollbar2.set)
        self.staged_list.bind("<MouseWheel>",lambda event : self.staged_list.yview("scroll",-event.delta/120,"units"))
        scrollbar2.config(command=self.staged_list.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.staged_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        

        # self.tracked_replays.grid(row=1,column=0,sticky="NSWE")
        # self.staged_list.grid(row=1,column=2,sticky="NSWE")
        f.grid(row=1,column=0,sticky="NSWE")
        f2.grid(row=1,column=2,sticky="NSWE")


        self.info = ReplayInfoFrame(frame)#tk.Frame(self,width=100,height=100)

        self.info.grid(row=1,column=1,rowspan=2,sticky="NS")

        self.tracked_replays.link(self.staged_list)
        self.staged_list.link(self.tracked_replays)
        self.staged_list.set_insert_callback(self.copy_to_staging)
        self.staged_list.set_delete_callback(self.delete_from_staging)

        frame.grid_columnconfigure(0,weight=1)
        frame.grid_columnconfigure(2,weight=1)
        frame.grid_rowconfigure(1,weight=1)

    def start_add_mode(self,frame):
        print "Addmode"
        tk.Label(frame,text="Untracked Replays").grid(row=0,column=0,sticky="NSWE")
        frame.replay_displayinfo = self.replay_display_edit
        f  = tk.Frame(frame)
        scrollbar = tk.Scrollbar(f, orient=tk.VERTICAL)
        self.untracked_replays = ReplayList(f,yscrollcommand=scrollbar.set)
        self.untracked_replays.bind("<MouseWheel>",lambda event : self.untracked_replays.yview("scroll",-event.delta/120,"units"))
        scrollbar.config(command=self.untracked_replays.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.untracked_replays.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        f.grid(row=1,column=0,sticky="NSWE")

        self.scan_and_fetch_untracked()


        self.edit_frame = ReplayEditFrame(frame)
        self.edit_frame.grid(row=1,column=1,sticky="NWSE")
        tk.Button(frame,text="rescan",command=self.scan_and_fetch_untracked).grid(row=2,column=0,sticky="WE")
        self.create_entry_button = tk.Button(frame,text="Track", command=self.track_selected_file)
        self.create_entry_button.grid(row=2,column=1,sticky="WE")

        frame.grid_rowconfigure(1,weight=1)
        frame.grid_columnconfigure(0,weight=1)
        frame.grid_columnconfigure(1,weight=1)


    def fetch_replays(self,replayfilters={},tagfilters={},playerfilters={},groupfilters={}):
        with DB_Manager() as mann:
            if replayfilters  or tagfilters or playerfilters or groupfilters:
                #print "dicts: ",replayfilters,tagfilters,playerfilters,groupfilters
                replays = mann.filter_replays(replayfilters,tagfilters,playerfilters,groupfilters)
            else:
                replays = mann.get_all("replays","date_time desc")
        if self.tracked_replays.size() > 0:
            self.tracked_replays.delete(0,self.tracked_replays.size())
        for replay in replays:
            self.tracked_replays.insert("end",replay[2],replay)

    def scan_and_fetch_untracked(self):
        p = rl_paths.demo_folder()
        

        if self.untracked_replays.size() > 0:
            self.untracked_replays.delete(0,self.untracked_replays.size())
        print "Scanning for new replays"
        with DB_Manager(debug=True) as dmann:
            for f in os.listdir(p):
                filename = os.path.splitext(f)[0]
                fullpath = p+"\\"+f
                stat = os.stat(fullpath)
                #print "On file: "+f
                if os.path.isfile(fullpath) and not dmann.replay_exists(filename):
                    #print "%s was not in database"%(filename)
                    try:
                        shutil.copy2(rl_paths.demo_folder(filename),rl_paths.untracked_folder(filename)) #Copy to untracked folder
                        shutil.copy2(rl_paths.demo_folder(filename),rl_paths.backup_folder(filename)) #Copy to backup folder
                        os.remove(fullpath) #Remove old copy
                        #print "Moved %s to untracked"
                    except Exception, e:
                        print "Error during file handling"
                        print e
                elif os.path.isfile(fullpath):
                    #print "%s existed in database"%(f)
                    var = dmann.get_all_where("replays",filename=("=",filename))[0]
                    self.staged_list.insert("end",var[2],var)

        untracked = rl_paths.untracked_folder()
        l = os.listdir(untracked)
        tdict = {}
        for f in l:
            data = replay_parser.ReplayParser().parse(rl_paths.untracked_folder(os.path.splitext(f)[0]))
            time = re.sub(":(\d\d)-"," \\1:",data['header']['Date'])
            tdict[f]=time


        l.sort(reverse=True,key=lambda x:tdict[x])
        #print l
        for f in l:
            filename = os.path.splitext(f)[0]
            fullpath = untracked+"\\"+f
            #data = replay_parser.ReplayParser().parse(fullpath)
            #time = re.sub(":(\d\d)-"," \\1:",data['header']['Date'])#datetime.datetime.fromtimestamp(os.path.getmtime(fullpath)).strftime("%Y-%m-%d %H:%M")
            self.untracked_replays.insert("end","Replay "+str(tdict[f]),(filename,tdict[f],fullpath))
                    
    def track_selected_file(self):
        # t1 = threading.Thread(target=self.edit_frame.create_entry)
        # t1.start()
        if len(self.untracked_replays.curselection()) == 1:
            self.edit_frame.create_entry()

        if  self.edit_frame.replay_entry:
            #print self.edit_frame.replay_entry
            shutil.move(rl_paths.untracked_folder(self.edit_frame.headers[0]),rl_paths.tracked_folder(self.edit_frame.headers[0]))
            self.untracked_replays.delete_selected()
            self.tracked_replays.insert(0,self.edit_frame.replay_entry[2],self.edit_frame.replay_entry)
            if self.untracked_replays.size() == 0:
                self.edit_frame.clear()

        # self.tracked_replays.insert(0,self.edit_frame.values[2],self.edit_frame.values)
        # self.untracked_replays.delete()

    def replay_display_edit(self,variables):
        print "Notified of edit display",variables
        self.edit_frame.display_new(list(variables))

    def replay_displayinfo(self,variables):
        print "Displaying new info",variables
        self.info.display_new(list(variables))

    def save(self):
        #print "Saved"
        self.info.save()

    def copy_to_staging(self,variables):
        if not os.path.isfile(rl_paths.demo_folder(variables[1])):
            shutil.copy2(rl_paths.tracked_folder(variables[1]),rl_paths.demo_folder(variables[1]))

        if not os.path.isfile(rl_paths.tracked_folder(variables[1])):
            shutil.copy2(rl_paths.demo_folder(variables[1]),rl_paths.tracked_folder(variables[1]))

        if not os.path.isfile(rl_paths.backup_folder(variables[1])):
            shutil.copy2(rl_paths.demo_folder(variables[1]),rl_paths.backup_folder(variables[1]))

    def delete_from_staging(self,variables_list):
        for variables in variables_list:
            try:
                os.remove(rl_paths.demo_folder(variables[1]))
            except WindowsError,e:
                print e #If there were duplicates in the list somehow we get a can't find error

    def unstage_all(self):
        if self.staged_list.size() == 0: return
        self.staged_list.delete(0,self.staged_list.size())

    def filter_replays(self):
        pop = FilterPopup( 
            winfo_rootc=(self.winfo_rootx(),self.winfo_rooty()),
            callback=self.fetch_replays)
        pop.title("Filter")


        

