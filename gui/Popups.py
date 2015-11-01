#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from db_manager import *
import re

class TagPopup(tk.Toplevel):
    def __init__(self,parent=None,**kw):
        self.taglist = kw.pop("taglist")
        self.infowidget = kw.pop("infowidget")
        tk.Toplevel.__init__(self,parent,**kw)
        self.grab_set()
        self.replay_id = self.infowidget.id
        self.title("Add tag for "+self.infowidget.headers[0])
        print "Id is: ",self.replay_id 
        namelabel = tk.Label(self,text="Tag name")
        timelabel = tk.Label(self,text="Replaytime (mm:ss)")

        self.tagname = tk.Entry(self)
        self.tagname.bind("<Return>",lambda e : self.tagstamp.focus_set())
        self.tagstamp = tk.Entry(self)
        self.tagstamp.bind("<Return>",lambda e : self.tag_add())
        self.tagname.focus_set()
        addbutton = tk.Button(self,text="Add",command=self.tag_add)

        namelabel.grid(row=0,column=0,sticky="NSWE")
        timelabel.grid(row=0,column=1,sticky="NSWE")
        self.tagname.grid(row=1,column=0,sticky="NSWE")
        self.tagstamp.grid(row=1,column=1,sticky="NSWE")

        addbutton.grid(row=3,column=0,columnspan=2,sticky="NSWE")

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.geometry("+%d+%d" % (self.infowidget.winfo_rootx()+50,
                                  self.infowidget.winfo_rooty()+50))

    def tag_add(self):
        tname = self.tagname.get()
        tstamp = self.tagstamp.get()
        with DB_Manager() as dmann:
            dmann.add_tag(self.replay_id,tname,tstamp)
            self.taglist.insert(tname,tstamp)
            self.taglist.see("end")
        self.tagname.delete(0,"end")
        self.tagstamp.delete(0,"end")
        self.tagname.focus_set()
    def close(self):
        pass

class TableRowEditPopup(tk.Toplevel):
    def __init__(self,parent=None,**kw):
        self.row_values = kw.pop("row_values",[])
        wroot_x,wroot_y = kw.pop("winfo_rootc",(0,0))
        self.done_callback = kw.pop("done_callback",None)
        tk.Toplevel.__init__(self,parent,**kw)
        self.notif = tk.StringVar()


        self.grab_set()
        label_col=0
        entry_col=1
        self.entries = []
        print self.row_values

        for (i,txt) in enumerate(["Player Name","Team","Goals","Saves","Shots","Assists","Score"]):
            print i,txt
            tk.Label(self,text=txt).grid(row=i,column=label_col,sticky="we")
            self.entries.append(tk.Entry(self))
            self.entries[i].grid(row=i,column=entry_col,sticky="we")
            if self.row_values and i < len(self.row_values)-1: #Skip the ID which is the first elem in row_values
                self.entries[i].insert("end",self.row_values[i+1])

        tk.Button(self,text="Done",command=self.done).grid(row=i+1,column=0,columnspan=2,sticky="we")
        tk.Label(self,textvariable=self.notif).grid(row=i+2,column=0,columnspan=2,sticky="we")
        
        self.entries[0].focus_set()    
        self.geometry("+%d+%d" % (wroot_x+50,
                                  wroot_y+50))
    def valid(self):
        print self.entries[0].get(),self.entries[1].get()
        valid = len(self.entries[0].get()) > 0
        valid &= re.match("^\d$",self.entries[1].get()) != None
        return valid

    def set_done_callback(self,callback):
        self.done_callback = callback

    def done(self):
        if not self.valid(): 
            self.notif.set("Invalid entries")
            return
        self.final_values = (None,)+tuple(map(lambda ent: ent.get() , self.entries))
        if self.done_callback:
            self.done_callback(self.final_values)
        self.destroy()

class FilterPopup(tk.Toplevel):

    filter_options = ["replay name","map name","player name",]

    def __init__(self,parent,**kw):
        tk.Toplevel.__init__(parent,**kw)