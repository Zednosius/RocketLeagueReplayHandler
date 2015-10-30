#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from db_manager import *


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

class FilterPopup(tk.Toplevel):

    filter_options = ["replay name","map name","player name",]

    def __init__(self,parent,**kw):
        tk.Toplevel.__init__(parent,**kw)