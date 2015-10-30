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


def tag_popup(taglist,infowidget):
    TagPopup(taglist=taglist,infowidget=infowidget)


class ReplayManager(tk.Frame):
    def __init__(self,parent, **kw):
        tk.Frame.__init__(self, parent, **kw)

        with DB_Manager() as mann:
            replays = mann.get_all("replays")
        # print replays
        tk.Label(self,text="Replays").grid(row=0,column=0,sticky="NS")
        tk.Button(self,text="Filter").grid(row=2,column=0,sticky="WE")
        tk.Label(self,text="Staged").grid(row=0,column=2,sticky="NS")


        f  = tk.Frame(self)
        f2 = tk.Frame(self)
        scrollbar = tk.Scrollbar(f, orient=tk.VERTICAL)
        Lb1 = DragDropList(f,yscrollcommand=scrollbar.set)
        Lb1.bind("<MouseWheel>",lambda event : Lb1.yview("scroll",-event.delta/120,"units"))
        scrollbar.config(command=Lb1.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        Lb1.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


        for replay in replays:
            Lb1.insert("end",replay[2],replay)
        
        scrollbar2 = tk.Scrollbar(f2, orient=tk.VERTICAL)
        Lb2 = DragDropList(f2,yscrollcommand=scrollbar2.set)
        Lb2.bind("<MouseWheel>",lambda event : Lb2.yview("scroll",-event.delta/120,"units"))
        scrollbar2.config(command=Lb2.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        Lb2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


        # Lb1.grid(row=1,column=0,sticky="NSWE")
        # Lb2.grid(row=1,column=2,sticky="NSWE")
        f.grid(row=1,column=0,sticky="NSWE")
        f2.grid(row=1,column=2,sticky="NSWE")


        self.info = ReplayInfoFrame(self,bg="green")#tk.Frame(self,width=100,height=100)

        self.info.grid(row=1,column=1,rowspan=2,sticky="NS")

        Lb1.link(Lb2)
        Lb2.link(Lb1)

        self.grid_columnconfigure(0,weight=1)
        # self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(1,weight=1)

    def replay_displayinfo(self,variables):
        self.info.use_headers(list(variables))
        self.info.init()

        



#http://stackoverflow.com/questions/1966929/tk-treeview-column-sort
def treeview_sort_column(tv, col, reverse,cast):
        l = [(cast(tv.set(k, col)), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
                   treeview_sort_column(tv, col, not reverse,cast))


class TagList(tk.Frame):
    def __init__(self,parent,**kw):
        self.mFont = kw.pop("mFont",tkFont.nametofont("TkDefaultFont"))
        tk.Frame.__init__(self,parent,kw)
        
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.tag_body = tk.Listbox(self, background="#F0F8FF",font=self.mFont, width=10,yscrollcommand=self.scrollbar.set)
        self.tag_body.bind("<MouseWheel>",lambda event : self.tag_body.yview("scroll",-event.delta/120,"units"))
        self.scrollbar.config(command=self.tag_body.yview)
        self.addbutton = tk.Button(self,text="Add tag",command=lambda taglist=self,parent=parent : tag_popup(taglist,parent))

        self.addbutton.grid(row=1,columnspan=2,stick="WE")#.pack(side=tk.BOTTOM,fill=tk.X,expand=1)
        self.scrollbar.grid(row=0,column=1,sticky="SN")#.pack(side=tk.RIGHT, fill=tk.Y)
        self.tag_body.grid(row=0,column=0,sticky="NSWE")#.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.grid_rowconfigure(0,weight=1)

    def insert(self,tagname,timestamp):
        self.tag_body.insert("end",tagname+" @ "+timestamp)
        self.tag_body.config(width=0)
    def see(self,index):
        self.tag_body.see(index)
    def delete(self,index,end):
        self.tag_body.delete(index,end)


        


        

