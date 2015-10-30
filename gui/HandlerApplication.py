#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from db_manager import *
from DragDropList import *
from Popups import *
from ReplayInfoFrame import *
from ReplayList import *

def tag_popup(taglist,infowidget):
    TagPopup(taglist=taglist,infowidget=infowidget)


class ReplayManager(tk.Frame):
    def __init__(self,parent, **kw):
        tk.Frame.__init__(self, parent, **kw)



        tk.Label(self,text="Replays").grid(row=0,column=0,sticky="NS")
        tk.Button(self,text="Filter").grid(row=2,column=0,sticky="WE")
        tk.Label(self,text="Staged").grid(row=0,column=2,sticky="NS")
        tk.Button(self,text="Unstage").grid(row=2,column=2,sticky="WE")
        
        f  = tk.Frame(self)
        f2 = tk.Frame(self)
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


        self.info = ReplayInfoFrame(self)#tk.Frame(self,width=100,height=100)

        self.info.grid(row=1,column=1,rowspan=2,sticky="NS")

        self.replay_list.link(self.staged_list)
        self.staged_list.link(self.replay_list)

        self.grid_columnconfigure(0,weight=1)
        # self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(1,weight=1)

    def fetch_replays(self,replayfilters={},tagfilters={},playerfilters={},groupfilters={}):

        with DB_Manager() as mann:
            replays = mann.filter_replays(replayfilters,tagfilters,playerfilters,groupfilters)

        for replay in replays:
            self.replay_list.insert("end",replay[2],replay)

    def replay_displayinfo(self,variables):
        #print "Displaying new info",variables
        self.info.display_new(list(variables))

        







        


        

