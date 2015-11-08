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
import time
import threading
import rl_paths
import replay_parser
import logging
import logging.config
from logging.handlers import RotatingFileHandler
# handler = RotatingFileHandler("log.log",mode='a',maxBytes=1024*1024*5,backupCount=3,encoding="Utf-8",delay=0)
# formatter = logging.Formatter("%(asctime)s %(name)s - %(levelname)s: %(message)s")
# handler.setFormatter(formatter)
# logging.basicConfig(stream=handler,level=logging.DEBUG)
logging.config.fileConfig("log.config")
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)

class ReplayManager(tk.Frame):
    def __init__(self,parent, **kw):
        logger.info("Creating Manager")
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
        logger.info("Manager created")



    def start_browse_mode(self,frame):
        logger.info("Creating browse tab")
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

        self.info.grid(row=1,column=1,rowspan=2,sticky="NSWE")

        self.tracked_replays.link(self.staged_list)
        self.staged_list.link(self.tracked_replays)
        self.staged_list.set_insert_callback(self.copy_to_staging)
        # self.staged_list.set_delete_callback(self.delete_from_staging)

        frame.grid_columnconfigure(0,weight=1)
        frame.grid_columnconfigure(1,weight=1)
        frame.grid_columnconfigure(2,weight=1)
        frame.grid_rowconfigure(1,weight=1)
        logger.info("Browse tab created")

    def start_add_mode(self,frame):
        logger.info("Creating add tab")
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
        logger.info("Add tab created")


    def fetch_replays(self,replayfilters={},tagfilters={},playerfilters={},groupfilters={}):
        logger.info("Fetching replays")
        with DB_Manager() as mann:
            if replayfilters  or tagfilters or playerfilters or groupfilters:
                replays = mann.filter_replays(replayfilters,tagfilters,playerfilters,groupfilters)
                logger.debug("Fetched replays from database with parameters %s %s %s %s",
                    replayfilters,tagfilters,playerfilters,groupfilters)
            else:
                replays = mann.get_all("replays","date_time desc")
                logger.debug("Fetched all replays (paramless)")

        if self.tracked_replays.size() > 0:
            self.tracked_replays.delete(0,self.tracked_replays.size())
            logger.info("Emptied tracked_replay list")

        for replay in replays:
            self.tracked_replays.insert("end",replay[2],replay)
        logger.info("Inserted replays into tracked_replay_list")


    def scan_demo_folder(self):
        self.demo_scan = []
        logger.info("Scanning demo on path %s",rl_paths.demo_folder())
        with DB_Manager(debug=True) as dmann:
            l = [rl_paths.demo_folder( os.path.splitext(x)[0]) 
                for x in os.listdir(rl_paths.demo_folder()) 
                if os.path.isfile(rl_paths.demo_folder(os.path.splitext(x)[0]))]
            l.sort(reverse=True,key=lambda x: os.path.getmtime(x))
            logger.info("Sorted replays by date")
            for f in l:
                filename = os.path.splitext(os.path.basename(f))[0]
                if os.path.isfile(f) and not dmann.replay_exists(filename):
                    self.demo_scan.append({"path":f,"name":filename,"tracked":False})
                elif os.path.isfile(f):
                    self.demo_scan.append({"path":f,"name":filename,"tracked":True})
                else:
                    pass
                logger.debug("Scanning %s resulted in %s",filename,self.demo_scan[-1])
        logger.info("Appended all %s replays",len(l))

    def move_new_replays_to_untracked(self):
        logger.info("Moving new replays to untracked folder")
        count = 0
        for entry in self.demo_scan:
            if not entry["tracked"]:
                count += 1
                try:
                    shutil.copy2(rl_paths.demo_folder(entry['name']),rl_paths.untracked_folder(entry['name'])) #Copy to untracked folder
                    if not os.path.isfile(rl_paths.backup_folder(entry['name'])):
                        shutil.copy2(rl_paths.demo_folder(entry['name']),rl_paths.backup_folder(entry['name'])) #Copy to backup folder
                        logger.info("Backed up replay %s", entry['name'])
                    os.remove(entry["path"]) #Remove old copy
                    logger.debug("Moved %s to untracked",entry['name'])
                except Exception, e:
                    logger.error("Error during move of file %s",entry['name'])
                    logger.error("Error was: %s",e)
        logger.info("Moved a total of %s replays to untracked folder",count)

    def insert_scanned_staged(self):
        logger.info("Inserting scanned staged files into staged list")
        count = 0
        with DB_Manager() as dmann:
            for entry in self.demo_scan:
                if entry['tracked']:
                    count += 1
                    var = dmann.get_all_where("replays",filename=("=",entry["name"]))[0]
                    if self.staged_list.size() == 0: 
                        self.staged_list.insert("end",var[2],var)
                    else:
                        for i,v in enumerate(self.staged_list.variables):
                            #Insert based on date
                            if v[4] < var[4]:
                                self.staged_list.insert(i,var[2],var)
                                break
                            elif i+1 == self.staged_list.size():
                                self.staged_list.insert("end",var[2],var)
                                break
                    logger.debug("Inserted staged replay %s",entry['name'])
        logger.info("Inserted total of %s staged replays",count)
        logger.info("Staged files insertion complete")

    def insert_untracked(self):
        logger.info("Inserting untracked files")
        untracked = rl_paths.untracked_folder()
        l = os.listdir(untracked)
        tdict = {}
        for f in l:
            path = rl_paths.untracked_folder(os.path.splitext(f)[0])
            data = replay_parser.ReplayParser().parse(path)
            #Correct the file modified time if it is discrepant with the internal date from the replay file.
            #A discrepancy most probably means the replay was downloaded from somewhere.
            #Correcting the time makes it easier to find it in the replay browser ingame, because it will line up with its staged counterpart
            repTime = time.mktime(datetime.datetime(*map(int,data['header']['Date'].replace(":","-").split("-"))).timetuple())
            ftime = os.path.getmtime(path)
            if repTime != ftime:
                os.utime(path,(repTime,repTime))
                logger.info("Changed time of %s to %s from %s",path,repTime,ftime)

            time_ = re.sub(":(\d\d)-"," \\1:",data['header']['Date'])
            tdict[f]=time_


        l.sort(reverse=True,key=lambda x:tdict[x])
        logger.info("Sorted after time")
        for f in l:
            filename = os.path.splitext(f)[0]
            fullpath = untracked+"\\"+f
            self.untracked_replays.insert("end","Replay "+str(tdict[f]),(filename,tdict[f],fullpath))
            logger.debug("Inserted replay %s",f)
        logger.info("Inserted total of %s untracked replays",len(l))
        logger.info("Insertion of untracked complete")

    def scan_and_fetch_untracked(self):
        logger.info("Beginning scan and fetch routine")
        self.scan_demo_folder()

        if self.untracked_replays.size() > 0:
            self.untracked_replays.delete(0,self.untracked_replays.size())
        if self.staged_list.size() > 0:
            self.staged_list.delete(0,self.staged_list.size())

        self.move_new_replays_to_untracked()
        self.insert_scanned_staged()
        self.insert_untracked()
        logger.info("Scan and fetch complete")

                    
    def track_selected_file(self):
        try:
            logger.info("Starting track routine")      
            self.edit_frame.create_entry()
            logger.info("EditFrame create entry done")
            if  hasattr(self.edit_frame,"replay_entry") and self.edit_frame.replay_entry != None:
                logger.info("Create Entry succesfull")
                src = rl_paths.untracked_folder(self.edit_frame.headers[0])
                dst = rl_paths.tracked_folder(self.edit_frame.headers[0])
                shutil.move(src,dst)
                logger.info("Moved from %s to %s",src,dst)
                self.tracked_replays.insert(0,self.edit_frame.replay_entry[2],self.edit_frame.replay_entry)

                self.untracked_replays.delete_selected()

                if self.untracked_replays.size() == 0:
                    self.edit_frame.clear()
                    logger.info("Cleared edit frame")
            logger.info("Replay %s now tracked",self.edit_frame.headers[0])
        except sqlite3.IntegrityError,e:
            logger.error("Error during replay insertion")
            logger.error("Error: %s",e)


    def replay_display_edit(self,variables):
        logger.info("Edit now displaying: %s",variables)
        self.edit_frame.display_new(list(variables))

    def replay_displayinfo(self,variables):
        logger.info("Info now displaying: %s",variables)
        self.info.display_new(list(variables))

    def save(self):
        self.info.save()

    def copy_to_staging(self,variables):
        if not os.path.isfile(rl_paths.demo_folder(variables[1])):
            shutil.copy2(rl_paths.tracked_folder(variables[1]),rl_paths.demo_folder(variables[1]))
            logger.info("Copied %s to demo_folder",variables[1])

        if not os.path.isfile(rl_paths.tracked_folder(variables[1])):
            shutil.copy2(rl_paths.demo_folder(variables[1]),rl_paths.tracked_folder(variables[1]))
            logger.info("Copied %s to tracked folder",variables[1])

        if not os.path.isfile(rl_paths.backup_folder(variables[1])):
            shutil.copy2(rl_paths.demo_folder(variables[1]),rl_paths.backup_folder(variables[1]))
            logger.info("Copied %s to backup folder",variables[1])

    def delete_from_staging(self,variables_list):
        for variables in variables_list:
            try:
                os.remove(rl_paths.demo_folder(variables[1]))
                logger.info("Unstaged replay %s",variables[1])
            except WindowsError,e:
                logger.error("Error unstaging file %s ",variables[1])
                logger.error("Error: %s",e)
                #If there were duplicates in the list somehow we get a can't find error

    def unstage_all(self):
        logger.info("Unstaging all staged replays")
        if self.staged_list.size() == 0: return
        self.delete_from_staging(self.staged_list.variables)
        self.staged_list.delete(0,self.staged_list.size())
        logger.info("Unstage all complete")

    def filter_replays(self):
        logger.info("Displaying filter popup")
        pop = FilterPopup( 
            winfo_rootc=(self.winfo_rootx(),self.winfo_rooty()),
            callback=self.fetch_replays)
        pop.title("Filter")
        

