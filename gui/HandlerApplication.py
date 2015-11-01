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
from os.path import expanduser
import errno



def make_dirs():
    try:
        os.makedirs(expanduser("~")+ReplayManager._default_path+"\\tracked")
        os.makedirs(expanduser("~")+ReplayManager._default_path+"\\untracked")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

class ReplayManager(tk.Frame):
    _default_path = "\Documents\My Games\Rocket League\TAGame\Demos"
    def __init__(self,parent, **kw):
        make_dirs()
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
        tk.Button(frame,text="Filter").grid(row=2,column=0,sticky="WE")
        tk.Label(frame,text="Staged").grid(row=0,column=2,sticky="NS")
        tk.Button(frame,text="Unstage").grid(row=2,column=2,sticky="WE")
        
        f  = tk.Frame(frame)
        f2 = tk.Frame(frame)
        scrollbar = tk.Scrollbar(f, orient=tk.VERTICAL)
        self.replay_list = ReplayList(f,yscrollcommand=scrollbar.set)
        self.replay_list.bind("<MouseWheel>",lambda event : self.replay_list.yview("scroll",-event.delta/120,"units"))
        scrollbar.config(command=self.replay_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.replay_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.fetch_replays()

        
        scrollbar2 = tk.Scrollbar(f2, orient=tk.VERTICAL)
        self.staged_list = ReplayList(f2,yscrollcommand=scrollbar2.set)
        self.staged_list.bind("<MouseWheel>",lambda event : self.staged_list.yview("scroll",-event.delta/120,"units"))
        scrollbar2.config(command=self.staged_list.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.staged_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        

        # self.replay_list.grid(row=1,column=0,sticky="NSWE")
        # self.staged_list.grid(row=1,column=2,sticky="NSWE")
        f.grid(row=1,column=0,sticky="NSWE")
        f2.grid(row=1,column=2,sticky="NSWE")


        self.info = ReplayInfoFrame(frame)#tk.Frame(self,width=100,height=100)

        self.info.grid(row=1,column=1,rowspan=2,sticky="NS")

        self.replay_list.link(self.staged_list)
        self.staged_list.link(self.replay_list)

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

        frame.grid_rowconfigure(1,weight=1)
        frame.grid_columnconfigure(0,weight=1)
        frame.grid_columnconfigure(1,weight=1)


    def fetch_replays(self,replayfilters={},tagfilters={},playerfilters={},groupfilters={}):
        with DB_Manager() as mann:
            replays = mann.filter_replays(replayfilters,tagfilters,playerfilters,groupfilters)

        for replay in replays:
            self.replay_list.insert("end",replay[2],replay)

    def scan_and_fetch_untracked(self):
        p = expanduser("~")+self._default_path
        untracked = p+"\\untracked"
        if self.untracked_replays.size() > 0:
            self.untracked_replays.delete(0,self.untracked_replays.size())

        print "Scanning for new replays"
        with DB_Manager(debug=True) as dmann:
            for f in os.listdir(p):
                filename = os.path.splitext(f)[0]
                fullpath = p+"\\"+f
                stat = os.stat(fullpath)
                print "On file: "+f
                if os.path.isfile(fullpath) and not dmann.replay_exists(filename):
                    print "%s was not in database"%(filename)
                    try:
                        shutil.copy2(fullpath,untracked+"\\"+f)
                        os.remove(fullpath)
                        print "Moved %s to untracked"
                    except Exception, e:
                        print "Error during file handling"
                        print e
                elif os.path.isfile(fullpath):
                    print "%s existed in database"%(f)
                    var = dmann.get_all_where("replays",filename=("=",filename))[0]
                    self.staged_list.insert("end",var[2],var)

        l = os.listdir(untracked)
        l.sort(reverse=True,key=lambda x:os.path.getctime(untracked+"\\"+x))
        for f in l:
            filename = os.path.splitext(f)[0]
            fullpath = untracked+"\\"+f
            time = datetime.datetime.fromtimestamp(os.path.getmtime(fullpath)).strftime("%Y-%m-%d-%H:%M")
            self.untracked_replays.insert("end","Replay "+str(time),(filename,time,fullpath))
                    

    def replay_display_edit(self,variables):
        self.edit_frame.display_new(list(variables))

    def replay_displayinfo(self,variables):
        #print "Displaying new info",variables
        self.info.display_new(list(variables))

    def save(self):
        print "Saved"
        self.info.save()







        


        

