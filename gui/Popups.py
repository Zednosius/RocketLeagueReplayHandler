#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import BetterTk as btk
import ttk
import tkFont
from db_manager import *
import re

import logging
logger = logging.getLogger(__name__)

class TagPopup(tk.Toplevel):
    def __init__(self,parent=None,**kw):
        logger.info("Made tagpopup")
        self.taglist = kw.pop("taglist")
        self.infowidget = kw.pop("infowidget")
        tk.Toplevel.__init__(self,parent,**kw)
        self.grab_set()
        self.focus_set()
        self.replay_id = self.infowidget.id
        self.title("Add tag for "+self.infowidget.headers[0])
        
        namelabel = tk.Label(self,text="Tag name")
        timelabel = tk.Label(self,text="Replaytime (mm:ss)")

        self.tagname = btk.Entry(self)
        self.tagname.bind("<Return>",lambda e : self.tagstamp.focus_set())
        self.tagstamp = btk.Entry(self)
        self.tagstamp.bind("<Return>",lambda e : self.tag_add())
        self.tagname.focus_set()
        addbutton = ttk.Button(self,text="Add",command=self.tag_add)

        namelabel.grid(row=0,column=0,sticky="NSWE")
        timelabel.grid(row=0,column=1,sticky="NSWE")
        self.tagname.grid(row=1,column=0,sticky="NSWE")
        self.tagstamp.grid(row=1,column=1,sticky="NSWE")

        addbutton.grid(row=3,column=0,columnspan=2,sticky="NSWE")

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.geometry("+%d+%d" % (self.infowidget.winfo_rootx()+50,
                                  self.infowidget.winfo_rooty()+50))
        logger.info("Tag popup created")

    def tag_add(self):
        logger.info("Adding tag")
        tname = self.tagname.get()
        tstamp = self.tagstamp.get()
        with DB_Manager() as dmann:
            dmann.add_tag(self.replay_id,tname,tstamp)
            self.taglist.insert(self.replay_id,tname,tstamp)
            self.taglist.see("end")
            logger.debug("Added tag %s @ %s",tname,tstamp)
        self.tagname.delete(0,"end")
        self.tagstamp.delete(0,"end")
        logger.info("Cleared entries")
        self.tagname.focus_set()
    def close(self):
        pass

class TableRowEditPopup(tk.Toplevel):
    def __init__(self,parent=None,**kw):
        self.id = kw.pop("replay_id",None)
        logger.info("Making row edit popup")
        self.row_values = kw.pop("row_values",[])
        logger.debug("Row values: %s",self.row_values)
        wroot_x,wroot_y = kw.pop("winfo_rootc",(0,0))
        self.done_callback = kw.pop("done_callback",None)
        tk.Toplevel.__init__(self,parent,**kw)
        self.notif = tk.StringVar()


        self.grab_set()
        self.focus_set()
        label_col=0
        entry_col=1
        self.entries = []
        print "row values: ",self.row_values

        for (i,txt) in enumerate(["Player Name","Team","Goals","Saves","Shots","Assists","Score"]):
            # print i,txt
            tk.Label(self,text=txt).grid(row=i,column=label_col,sticky="we")
            self.entries.append(btk.Entry(self))
            self.entries[i].grid(row=i,column=entry_col,sticky="we")
            if self.row_values and i < len(self.row_values)-1: #Skip the ID which is the first elem in row_values
                self.entries[i].insert("end",self.row_values[i+1])
                logger.debug("Inserted on %s: %s",i,self.row_values[i+1])
        ttk.Button(self,text="Done",command=self.done).grid(row=i+1,column=0,columnspan=2,sticky="we")
        tk.Label(self,textvariable=self.notif).grid(row=i+2,column=0,columnspan=2,sticky="we")
        
        self.entries[0].focus_set()    
        self.geometry("+%d+%d" % (wroot_x+50,
                                  wroot_y+50))
        logger.info("Popup created")

    def valid(self):
        logger.info("Check if valid")
        valid = len(self.entries[0].get()) > 0
        valid &= re.match("^\d$",self.entries[1].get()) != None
        logger.info("Input valid status: %s",valid)
        return valid

    def set_done_callback(self,callback):
        self.done_callback = callback

    def done(self):
        if not self.valid(): 
            self.notif.set("Invalid entries")
            return
        self.final_values = (self.id,)+tuple(map(lambda ent: ent.get() , self.entries))
        logger.debug("Row values edited to: %s",self.final_values)
        if self.done_callback:
            self.done_callback(self.final_values)
        self.destroy()

class FilterPopup(tk.Toplevel):

    filter_options ={
        "replayfilters":["Map","Date"],
        "tagfilters":   ["Tag"],
        "playerfilters":["Player","Goals","Saves"],
        "groupfilters":["Group Name"],
        }
    db_translate={"Player":"playername","Date":"date_time","Group Name":"name"}
    last_filters = {}
    def __init__(self,parent=None,**kw):
        logger.info("Making filter popup")
        self.callback = kw.pop("callback",None)
        wroot_x,wroot_y = kw.pop("winfo_rootc",(0,0))
        tk.Toplevel.__init__(self,parent,**kw)
        self.grab_set()
        self.focus_set()

        self.entries = {}
        idx = 0
        print "Filters last time",FilterPopup.last_filters
        for filtertype, options in self.filter_options.items():             
            for option in options:              
                tk.Label(self,text=option).grid(row=idx,column=0)
                self.entries[option] = (btk.Entry(self))
                self.entries[option].grid(row=idx,column=1,sticky="we")
                self.entries[option].insert(0, self.last_filters.get(filtertype,{}).get(self.db_translate.get(option,option),("",""))[1])
                idx += 1

        ttk.Button(self,text="Apply",command=self.done).grid(row=idx+1,column=0,columnspan=2,sticky="we")
        self.grid_columnconfigure(1,weight=1)
        self.geometry("+%d+%d" % (wroot_x+50, wroot_y+50))
        logger.info("Filter popup done")

    def done(self):
        logger.info("Clicked done on filterpopup")
        filters = {}

        for filtertype, options in self.filter_options.items():
            filters[filtertype] = {}
            for option in options:
                if self.entries[option].get() != "":
                      filters[filtertype][self.db_translate.get(option,option)] = ("=",self.entries[option].get())
        logger.debug("Filters chosen were: %s ",filters)
        FilterPopup.last_filters = dict(filters)
        if self.callback:
            logger.info("calling callback with filters")
            self.callback(**filters)
        self.destroy()

class AddToGroupPopup(tk.Toplevel):

    def __init__(self,parent=None,**kw):
        logger.info("Making group popup")
        self.callback = kw.pop("callback",None)
        wroot_x,wroot_y = kw.pop("winfo_rootc",(0,0))
        self.grouplist = kw.pop("grouplist",[])
        self.replay_id = kw.pop("replay_id",-1)

        tk.Toplevel.__init__(self,parent,**kw)
        self.grab_set()
        self.focus_set()
        
        with DB_Manager() as dmann:
            groups = dmann.get_all("groups")
        self.combovalues = [group[1] for group in groups]
        logger.debug("Groups already added: %s",groups)
        self.label = tk.Label(self,text="Groups")
        self.combobox = ttk.Combobox(self,values=self.combovalues)
        self.combobox.bind("<Control-a>",lambda e: (self.combobox.select_range(0,tk.END),"break")[1])
        self.addbutton = ttk.Button(self,text="Add",command=self.add)

        self.label.grid(row=0,column=0,sticky="we")
        self.combobox.grid(row=1,column=0,sticky="we")
        self.addbutton.grid(row=2,column=0,sticky="we")



        self.geometry("+%d+%d" % (wroot_x+50, wroot_y+50))
        logger.info("Group popup created")

    def add(self):
        logger.info("Adding to group: %s",self.combobox.get())
        gname  =self.combobox.get()
        with DB_Manager() as dmann:

            group = dmann.get_all_where("groups",name=("=",unicode(gname)))
            
            if not group:
                logger.info("Group not found; Adding to database")
                c = dmann.add_group(gname)
                g_id = c.lastrowid
            else:
                logger.info("Group found in database")
                g_id = group[0][0]
            try:
                dmann.add_replay_to_group(self.replay_id, g_id)
                logger.info("Adding replay to group")
                self.combovalues.append(gname)
                self.grouplist.insert(self,replay_id, gname)
                logger.info("Inserted to combobox and list")
            except sqlite3.IntegrityError,e:
                logger.info("Replay was already a member of group: %s",gname)
                print "Duplicate group... aborting" #Cannot add replay to same group twice.      
        logger.info("Add to group done")
    def done(self):
        pass

class ConfirmPopup(tk.Toplevel):
    def __init__(self,parent=None,**kw):
        logger.info("Making Confirm popup")
        self.callback = kw.pop("callback",None)
        self.text = kw.pop("text","")
        wroot_x,wroot_y = kw.pop("winfo_rootc",(0,0))
        tk.Toplevel.__init__(self,parent,**kw)
        self.grab_set()
        self.focus_set()
        self.label = tk.Label(self,text=self.text)
        self.yesButton = ttk.Button(self,text="Yes",command=self.confirm)
        self.noButton = ttk.Button(self,text="No",command=self.abort)

        self.label.grid(row=0,column=0,columnspan=3)
        self.yesButton.grid(row=1,column=0)
        self.noButton.grid(row=1,column=2)
        self.geometry("+%d+%d" % (wroot_x+50, wroot_y+50))
        logger.info("Confirm popup created")

    def confirm(self):
        if self.callback:
            logger.info("Calling callback")
            self.callback()
            self.destroy()

    def abort(self):
        self.destroy()



class ExportPopup(tk.Toplevel):
    def __init__(self,parent=None,**kw):
        self.callback = kw.pop("callback",None)
        self.listitems = kw.pop("listitems", [])
        wroot_x,wroot_y = kw.pop("winfo_rootc",(0,0))
        tk.Toplevel.__init__(self,parent,**kw)
        self.grab_set()
        self.focus_set()



        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.list = tk.Listbox(self,yscrollcommand=scrollbar.set,selectmode=tk.MULTIPLE)
        self.list.bind("<MouseWheel>",lambda event : self.list.yview("scroll",-event.delta/120,"units"))
        scrollbar.config(command=self.list.yview)
        


        self.export = tk.Button(self,text="Export",command=self.done)
        for item in self.listitems:
            self.list.insert("end", item[2])
        self.list.configure(height=15)
        self.list.grid(row=0,column=0,sticky="nswe")
        self.export.grid(row=1,column=0,sticky="wNSe")
        scrollbar.grid(row=0,column=1,rowspan=2,sticky="ns")
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.geometry("+%d+%d" % (wroot_x+50, wroot_y+50))
        logger.info("Confirm popup created")


    def done(self):
        print self.list.curselection()
        self.selection = [self.listitems[int(x)] for x in self.list.curselection()]
        self.destroy()

