#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import Tkinter as tk
import ttk
import tkFont
from db_manager import *
import sqlite3
import replay_parser
import re
import shutil
import rl_paths

class ReplayEditFrame(tk.Frame):
    def __init__(self,parent,**kw):
        self.mFont = tkFont.Font(family="Helvetica",size=14)
        tk.Frame.__init__(self,parent,kw)
        self.notif_text = tk.StringVar()
        self.notif = tk.Label(self,textvariable=self.notif_text,fg="#DD0000")
        self.notif.grid(row=0,column=1,sticky="we")
        label_row = 1
        entry_row = 2

        tk.Label(self,text="Name").grid(row=label_row,column=0)
        tk.Label(self,text="Map name").grid(row=label_row,column=1)
        tk.Label(self,text="Date").grid(row=label_row,column=2)
        
        self.name = tk.Entry(self)
        self.name.grid(row=entry_row,column=0,sticky="we")
        self.mapname = tk.Entry(self)
        self.mapname.grid(row=entry_row,column=1,sticky="we")
        self.date= tk.Entry(self)
        self.date.grid(row=entry_row,column=2,sticky="we")

        self.table = ttk.Treeview(self)

        self.allcols = ["#1","#2","#3","#4","#5","#6","#7"]
        self.table["columns"] = self.allcols
        style = ttk.Style(self)
        style.configure('Treeview', rowheight=40)
        self.table['show'] = 'headings'
        self.table.heading("#1", text="Player")
        self.table.heading("#2", text="Team"  )
        self.table.heading("#3", text="Goals" )
        self.table.heading("#4", text="Saves" )
        self.table.heading("#5", text="Shots" )
        self.table.heading("#6", text="Assists" )
        self.table.heading("#7", text="Score" )
        for col in self.allcols:
            self.table.column(col,anchor='center',minwidth=75,width=75)
        self.table.column('#1',anchor='center',minwidth=100,width=100)

        self.table.grid(row=entry_row+1,column=0,columnspan=4,sticky="NEWS")
        
        

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_columnconfigure(3,weight=1)

    def display_new(self,variables):
        data = replay_parser.ReplayParser().parse(variables[2])
        self.headers = variables
        self.values = []
        print self.headers
        #New replay
        if 'PlayerStats' in data['header'].keys():
            self.notif_text.set("There might be missing data, doublecheck")
            for ps in data['header']['PlayerStats']:
                self.values.append((None,ps['Name'].decode('unicode-escape'),ps['Team'],ps['Goals'],ps['Saves'],ps['Shots'],ps['Assists'],ps['Score']))

        else:
            self.notif_text.set("Old replay format, might be missing data")
            names_goals = {}
            for d in data['header']['Goals']:
                names_goals[d['PlayerName'].decode('unicode-escape')] = (1 + names_goals.get("PlayerName",[0])[0],d['PlayerTeam'])
            

            for k,v in names_goals.items():
                self.values.append((None,k,int(names_goals[k][1]),names_goals[k][0]))
        self.name.delete(0,"end")
        self.mapname.delete(0,"end")
        self.date.delete(0,"end")

        self.name.insert(0,"Replay "+self.headers[1])
        self.mapname.insert(0,data['header']['MapName'])
        self.date.insert(0,self.headers[1])
        self.table_insert_values()

    def table_insert_values(self):
        """Inserts all values in self.values into the table"""
        self.table.delete(*self.table.get_children())

        for values in self.values:
            self.table.insert("", "end",
             values=values[1:],
             tags=("orange" if int(values[2]) == 1 else "blue"))

            if(self.table.column("#1","width") < self.mFont.measure(values[1])): #Adjust table column size if needed
                self.table.column("#1",width=int(self.mFont.measure(values[1])*1.2))

        self.table.tag_configure('orange' , background='#FF7F00',font=self.mFont)
        self.table.tag_configure('blue', background='#82CFFD',font=self.mFont)

    def create_entry(self):
        if not self.valid(): return
        replay_name = self.name.get() 
        map_name    = self.mapname.get()
        date        = self.date.get()
        try:
            with DB_Manager() as dmann:
                c = dmann.add_replay(filename=self.headers[0],name=replay_name, mapname=map_name, date_time=date)
                idx = c.lastrowid
                self.replay_entry = (idx,self.headers[0],replay_name,map_name,date)
                for values in self.values:
                    print idx,values
                    dmann.add_team(idx,*(values[1:]))
                dmann.add_note(idx,"")
        except sqlite3.IntegrityError, e:
            self.notif_text.set("ERROR: COULD NOT CREATE ENTRY\n"+str(e))

    def valid(self):
        date = self.date.get()
        if not re.match("\d{4}-\d{2}-\d{2} \d{2}:\d{2}",date):
            self.notif_text.set("Date format must be YYYY-MM-DD hh:mm")
            return False


        return True

    def edit_row(self, rowindex):
        pass
