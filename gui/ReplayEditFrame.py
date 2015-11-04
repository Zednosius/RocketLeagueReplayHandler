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
import Popups
import names
class ReplayEditFrame(tk.Frame):
    def __init__(self,parent,**kw):
        self.mFont = tkFont.Font(family="Helvetica",size=14)
        tk.Frame.__init__(self,parent,kw)

        ##### Widget Creation ######
        self.notif_text = tk.StringVar()
        self.notif      = tk.Label(self,textvariable=self.notif_text,fg="#DD0000")
        self.name       = tk.Entry(self)    
        self.mapname    = tk.Entry(self)       
        self.date       = tk.Entry(self)
        self.table      = ttk.Treeview(self)

        self.add_empty_row_button = tk.Button(self,text="Add row",command=self.add_empty_row)
        namelabel = tk.Label(self,text="Name")
        maplabel  = tk.Label(self,text="Map name")
        datelabel = tk.Label(self,text="Date")

        ############################

        self.prepare_table()
    


        #### Widget Positioning ####
        label_row = 1
        entry_row = 2

        namelabel.grid(row=label_row,column=0)
        maplabel. grid(row=label_row,column=1)
        datelabel.grid(row=label_row,column=2)

        self.notif.  grid(row=0,column=1,sticky="we")
        self.name.   grid(row=entry_row,column=0,sticky="we")
        self.mapname.grid(row=entry_row,column=1,sticky="we")
        self.date.   grid(row=entry_row,column=2,sticky="we")
        self.table.  grid(row=entry_row+1,column=0,columnspan=4,sticky="NEWS")
        self.add_empty_row_button.grid(row=entry_row+2,column=0,columnspan=4,sticky="NWE")
        ############################

        ##### Grid configuring #####
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_columnconfigure(3,weight=1)

    def prepare_table(self):
        #Adjust table row height
        style = ttk.Style(self)
        style.configure('Treeview', rowheight=40)

        self.allcols = ["#1","#2","#3","#4","#5","#6","#7"]
        self.table["columns"] = self.allcols      
        self.table['show'] = 'headings'
        self.table_headings = ["Player","Team","Goals","Saves","Shots","Assists","Score"]

        #Create table headings
        for (idx,txt) in enumerate(self.table_headings):
            self.table.heading("#"+str(idx+1), text=txt)

        #Adjust column sizes
        for col in self.allcols:
            self.table.column(col,anchor='center',minwidth=75,width=75)

        self.table.column('#1',anchor='center',minwidth=100,width=100)
        self.table.bind("<<TreeviewSelect>>",self.edit_row)



    def display_new(self,variables):
        """
        Uses the variables provided to redraw this frame with the new information.
        """
        data = replay_parser.ReplayParser().parse(variables[2])
        self.headers = variables
        self.values = []

        print "\nDisplaying new"
        #New replay
        if 'PlayerStats' in data['header'].keys():
            self.notif_text.set("There might be missing data, doublecheck")
            for ps in data['header']['PlayerStats']:
                self.values.append(
                    (None,ps.get('Name', None).decode('unicode-escape'),
                        ps.get('Team', None),
                        ps.get('Goals', None),
                        ps.get('Saves', None),
                        ps.get('Shots', None),
                        ps.get('Assists', None),
                        ps.get('Score', None))
                    )
            print self.values
        else:
            #Old replay
            self.notif_text.set("Old replay format, might be missing data")
            names_goals = {}
            for d in data['header']['Goals']:
                if "PlayerName" in d:
                    names_goals[d['PlayerName'].decode('unicode-escape')] = (1 + names_goals.get("PlayerName",[0])[0],d['PlayerTeam'])
            
            for k,v in names_goals.items():
                self.values.append((None,k,int(names_goals[k][1]),names_goals[k][0])+("",)*4)

        print "Clearing self"
        self.clear()
        print "Inserting new"
        self.name.insert(0,"Replay "+self.headers[1])
        self.mapname.insert(0,names.stadiums.get(data['header']['MapName'].lower(),data['header']['MapName']))
        self.date.insert(0,re.sub(":(\d\d)-"," \\1:",data['header']['Date']))
        self.table_insert_values()
        print "Finished inserting values into table\n"

    def table_insert_values(self):
        """Inserts all values in self.values into the table"""
    
        for values in self.values:
            self.table.insert("", "end",
             values=values[1:],
             tags=("orange" if int(values[2]) == 1 else "blue"))

            if(self.table.column("#1","width") < self.mFont.measure(values[1])): #Adjust table column size if needed
                self.table.column("#1",width=int(self.mFont.measure(values[1])*1.2))

        self.table.tag_configure('orange' , background='#FF7F00',font=self.mFont)
        self.table.tag_configure('blue',    background='#82CFFD',font=self.mFont)
        self.table.tag_configure('new_row', background='#00ff00',font=self.mFont)

    def clear(self):
        self.table.delete(*self.table.get_children())
        self.name.delete(0,"end")
        self.mapname.delete(0,"end")
        self.date.delete(0,"end")
        self.replay_entry = None

    def create_entry(self):
        if not self.valid(): return

        replay_name = self.name.get() 
        map_name    = self.mapname.get()
        date        = self.date.get()
        print "Creating entry"
        try:
            with DB_Manager(debug=True) as dmann:
                #Create a replay entry and get the id.

                c = dmann.add_replay(filename=self.headers[0],name=replay_name, mapname=map_name, date_time=date)
                idx = c.lastrowid
                self.replay_entry = (idx,self.headers[0],replay_name,map_name,date)
                print "Created: ",self.replay_entry

                #Make list of tuples to be inserted into database
                print "Inserting teams: ",[(idx,)+values[1:] for values in self.values]
                dmann.add_many_team([(idx,)+values[1:] for values in self.values])
                dmann.add_note(idx,"")
                self.notif_text.set("Replay added")

        except sqlite3.IntegrityError, e:
            self.notif_text.set("ERROR: COULD NOT CREATE ENTRY\n"+str(e))
            raise

    def valid(self):
        date = self.date.get()
        if not re.match("\d{4}-\d{2}-\d{2} \d{2}:\d{2}",date):
            self.notif_text.set("Date format must be YYYY-MM-DD hh:mm")
            return False
        for values in self.values:
            if values[1] == None or values[2] == None:
                self.notif_text.set("Name and Team must be entered")
                return False
        return True

    def edit_row(self,event):
        #Get selected row
        selection = self.table.selection()[0]
        row_index = self.table.index(selection)
        vals = []
        #If row_index is smaller than amount of rows we take that rows values
        #So that they are pre entered when the popup appears
        if row_index < len(self.values):
            vals = self.values[row_index]

        print "Creating edit popup for ",vals
        #Create the edit popup.
        popup = Popups.TableRowEditPopup(self,row_values=vals,winfo_rootc=(self.winfo_rootx(),self.winfo_rooty()))
        popup.set_done_callback(lambda vals_ : self.replace_row(selection,vals_))

    def add_empty_row(self):
        """Inserts an empty row at the end of the table.
        """
        self.table.insert("", "end",
             values= ("",)*len(self.allcols),
             tags=("new_row"))

    def replace_row(self,row_selection,vals):
        """
        Replaces the row identified by row_selection with the values from vals.
        """
        for (idx,heading) in enumerate(self.allcols):
            self.table.set(row_selection,heading,vals[idx+1])
        idx = self.table.index(row_selection)
        if idx < len(self.values):
            print "Replacing %s with %s" %(self.values[idx],vals)
            self.values[idx] = vals

        else:
            print "Appending",vals
            self.values.append(vals) 
