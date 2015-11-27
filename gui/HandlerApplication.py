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
import copy
import threading
import rl_paths
import replay_parser
import logging
import logging.config
from logging.handlers import RotatingFileHandler

import tasks

logging.config.fileConfig("log.config")
logger = logging.getLogger(__name__)





class ReplayManager(tk.Frame):
    def __init__(self,parent, **kw):
        logger.info("Creating Manager")
        rl_paths.make_dirs()
        tk.Frame.__init__(self, parent, **kw)
        n = ttk.Notebook(self)
        f1 = tk.Frame(n)   # first page, which would get widgets gridded into it
        f2 = tk.Frame(n)   # second page
        n.add(f1, text='browse',sticky="nswe")
        #n.add(f2, text='add',sticky="nswe")
        n.pack(fill="both",expand=1)
        self.start_browse_mode(f1)
        #self.start_add_mode(f2)
        # if(self.tracked_replays.size() == 0):
        #     n.select(1)
        logger.info("Manager created")



    def start_browse_mode(self,frame):
        logger.info("Creating browse tab")
        tk.Label(frame,text="Replays").grid(row=0,column=0,sticky="NS")
        ttk.Button(frame,text="Filter", command=self.filter_replays).grid(row=2,column=0,sticky="WE")
        tk.Label(frame,text="Staged").grid(row=0,column=2,sticky="NS")
        ttk.Button(frame,text="Unstage",command=self.unstage_all).grid(row=2,column=2,sticky="WE")
        
        f  = tk.Frame(frame)
        f2 = tk.Frame(frame)
        scrollbar = ttk.Scrollbar(f, orient=tk.VERTICAL)
        self.tracked_replays = ReplayList(f,yscrollcommand=scrollbar.set,exportselection=0)
        self.tracked_replays.bind("<MouseWheel>",lambda event : self.tracked_replays.yview("scroll",-event.delta/120,"units"))
        self.tracked_replays.bind("<Delete>", lambda e : self.delete_tracked_replay_popup())
        scrollbar.config(command=self.tracked_replays.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tracked_replays.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        #self.process_new()
        self.startup_procedure()
        print "After fetch"
        
        scrollbar2 = ttk.Scrollbar(f2, orient=tk.VERTICAL)
        self.staged_list = ReplayList(f2,yscrollcommand=scrollbar2.set)
        self.staged_list.bind("<MouseWheel>",lambda event : self.staged_list.yview("scroll",-event.delta/120,"units"))
        self.staged_list.bind("<Delete>", lambda event :self.staged_list.delete_selected())
        scrollbar2.config(command=self.staged_list.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.staged_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        #Remember to undo these comments later.
        self.staged_list.set_insert_callback(self.copy_to_staging)
        self.staged_list.set_delete_callback(self.delete_from_staging)

        # self.tracked_replays.grid(row=1,column=0,sticky="NSWE")
        # self.staged_list.grid(row=1,column=2,sticky="NSWE")
        f.grid(row=1,column=0,sticky="NSWE")
        f2.grid(row=1,column=2,sticky="NSWE")


        self.info = ReplayInfoFrame(frame)#tk.Frame(self,width=100,height=100)
        print "Info grid"
        self.info.grid(row=1,column=1,rowspan=2,sticky="NSWE")

        self.tracked_replays.link(self.staged_list)
        self.staged_list.link(self.tracked_replays)
        
        frame.grid_columnconfigure(0,weight=1)
        frame.grid_columnconfigure(1,weight=1)
        frame.grid_columnconfigure(2,weight=1)
        frame.grid_rowconfigure(1,weight=1)
        logger.info("Browse tab created")


    def replay_insert(self, replay_tup):
        replay = replay_tup[0]
        staged = replay_tup[1]
        self.tracked_replays.insert("end",replay[2],replay)
        if staged:
            self.staged_list.insert("end",replay[2],replay)

    def process_new(self):
        self.fetch_task = tasks.start_task(self,None,tasks.scan_refresh)

    def startup_procedure(self):
        self.fetch_task = tasks.start_task(self,self.replay_insert, tasks.startup_procedure)

    def fetch_replays(self,replayfilters={},tagfilters={},playerfilters={},groupfilters={}):
        #Stop the active task (has no effect if it already is stopped)
        if self.fetch_task:
            self.fetch_task[1].stopnow = True
        #Make sure the thread is stopped.
        self.fetch_task[0].join()
        #Clear the replay list
        if self.tracked_replays.size() > 0:
            self.tracked_replays.delete(0,self.tracked_replays.size())
            logger.info("Emptied tracked_replay list")
        #Start task for fetching with filters.
        self.fetch_task = tasks.start_task(self,self.replay_insert,tasks.fetch_replays,replayfilters,tagfilters,playerfilters,groupfilters)

    def replay_displayinfo(self,replay_headers):
        logger.info("Info now displaying: %s",replay_headers)
        self.info.clear()
        tasks.start_task(self,self.info.display,tasks.fetch_display_data,replay_headers)
        # self.info.display(list(replay_headers))

    def save(self):
        self.info.save()

    def copy_to_staging(self,variables_list):
        #print "Starting task: COPY TO STAGING"
        tasks.start_task(self,None,tasks.copy_to_staging,variables_list)


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
        #self.delete_from_staging(self.staged_list.variables)
        self.staged_list.delete(0,self.staged_list.size())
        logger.info("Unstage all complete")

    def filter_replays(self):
        logger.info("Displaying filter popup")
        pop = FilterPopup( 
            winfo_rootc=(self.winfo_rootx(),self.winfo_rooty()),
            callback=self.fetch_replays)
        pop.title("Filter")

    def delete_tracked_replay_popup(self):
        if(self.tracked_replays.size() == 0): return
        logger.info("Asking about deletion of replay")
        pop = ConfirmPopup(text="Are you sure you want to delete this replay?\nThis is permanent and your original data can not be recovered", 
            winfo_rootc=(self.winfo_rootx(),self.winfo_rooty()),
            callback=self.delete_tracked_replay
            )
        pop.title("Delete")

    def delete_tracked_replay(self):
        varlist = self.tracked_replays.get_variables(self.tracked_replays.selected_item)
        self.tracked_replays.delete_selected()
        logger.debug("DELETING: %s",varlist)
        with DB_Manager() as dmann:
            dmann.delete_replay(varlist[0])
        os.remove(rl_paths.tracked_folder(varlist[1]))
        if self.tracked_replays.size() == 0:
            self.info.clear()
        logger.info("Deleted replay")

    def edit(self):
        if self.info.displaydata == None: return
        top = tk.Toplevel()
        top.geometry("+%d+%d" % (self.winfo_rootx()+50,
                                  self.winfo_rooty()+50))
        top.grab_set()
        ed = ReplayEditFrame(top)
        sb = ttk.Button(top,text="Save",command=lambda : self.save_edit_changes(ed,top))
        ed.pack(fill="both")
        sb.pack(fill="both")
        ed.original_data = copy.deepcopy((self.info.displaydata))
        ed.display_new(copy.deepcopy((self.info.displaydata)))

    def save_edit_changes(self,editframe,top):
        if editframe.valid():
            logger.info("Beginning replay update")
            
            
            tasks.start_task(self,self.display_new,tasks.edit_update,editframe.original_data, editframe.replay_entry)
            top.destroy()
            
            logger.info("Updated replay")

    def display_new(self,updated):
        self.replay_displayinfo(updated['headers'])
        self.tracked_replays.replace_selected(updated['headers'])





