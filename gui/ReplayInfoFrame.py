#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from Popups import *
from db_manager import *


def tag_popup(taglist,infowidget):
    TagPopup(taglist=taglist,infowidget=infowidget)

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

class ReplayInfoFrame(tk.Frame):

    def motion(self,event):

        return "break"

    def make_table(self):
        
        self.table.bind_class(self.table,"<B1-Motion>",self.motion)


        self.allcols = ["#1","#2","#3","#4"]
        self.table["columns"] =["#1","#2","#3","#4"]
        style = ttk.Style(self)
        style.configure('Treeview', rowheight=40)
        self.table['show'] = 'headings'
        #Set up headings
        self.table.heading("#1", text="Player",command=lambda:treeview_sort_column(self.table, "#1", False,str))
        self.table.heading("#2", text="Team"  ,command=lambda:treeview_sort_column(self.table , "#2", False,int))
        self.table.heading("#3", text="Goals" ,command=lambda:treeview_sort_column(self.table, "#3", False,int))
        self.table.heading("#4", text="Saves" ,command=lambda:treeview_sort_column(self.table, "#4", False,int))
        for col in self.allcols:
            self.table.column(col,anchor='center',minwidth=75,width=75,stretch=True)
        self.table.column("#1",anchor='center',minwidth=100,width=100,stretch=True)
        #Remove the first column
        self.table.column("#0",width=0,minwidth=0)
        self.table_insert_values()
       # print "wh",self.table.winfo_width(),self.table.winfo_height()

    def table_insert_values(self):
        print self.values
        """Inserts all values in self.values into the table"""
        self.table.delete(*self.table.get_children())
    
        for values in self.values:
            self.table.insert("", "end",
             values=values[1:],
             tags=("red" if int(values[2]) == 1 else "blue"))

            if(self.table.column("#1","width") < self.mFont.measure(values[1])): #Adjust table column size if needed
                self.table.column("#1",width=int(self.mFont.measure(values[1])*1.2))
                #print "Adjusted columnsize"
        

        self.table.tag_configure('red' , background='#FF7F00',font=self.mFont)
        self.table.tag_configure('blue', background='#82CFFD',font=self.mFont)

    def populate_headers(self):
        """Inserts all header texts from self.headers"""
        added = False
        for i in range(0,len(self.headers)):
            # print "headr: ",self.headers[i]
            if(len(self.headervars) > i):
                self.headervars[i].set(self.headers[i])
            else:
                lbl = self.add_header_label(self.headers[i])
                added = True
                   
        
    def display_new(self, headers):
        self.save()

        if len(self.headers)+2 == len(headers):
            same = headers[0] == self.id and headers[1] == self.filename
            for i in range(0,len(self.headers)):
                #print "%s == %s = %s",self.headers[i] , headers[i+2],self.headers[i] == headers[i+2]
                same = self.headers[i] == headers[i+2] and same
            #print "same? : ",same
            if same: return

        self.use_headers(headers)
        self.init()

    def save(self):
        #Save old notes
        if len(self.headers) != 0:
            with DB_Manager() as dmann:
                dmann.update_note(self.id,self.note_body.get("1.0","end-1c"))
                self.cached[self.id]["notes"] = [(self.id,self.note_body.get("1.0","end-1c"),)]


    def use_headers(self,headers):


        """Uses the headers provided, replacing the old ones"""
        
        if headers:  
            if headers[0] not in self.cached:
                self.cached[headers[0]] = {"h":list(headers)}
                # print "Cached on ",headers[0]
                self.cache_order.append(headers[0])
                if len(self.cache_order) > 10:
                    self.cached.pop(self.cache_order.pop(0))

            self.headers = headers

            self.id = self.headers.pop(0)
            self.filename = self.headers.pop(0)
            if(len(self.headervars) == len(self.headers)):
                self.populate_headers()

    def load_values_from_db(self):
        """Load data from database"""
        # print "in cache: ",self.cached[self.id]
        if "values" in self.cached[self.id]:
            self.values = self.cached[self.id]["values"]
            self.tags = self.cached[self.id]["tags"]
            self.notes = self.cached[self.id]["notes"]
            # print "Fetched cached!"
            return 

        with DB_Manager() as mann:
            self.values = mann.get_all_where("teams",id=("=",self.id))
            self.tags = mann.get_all_where("tags",id=("=",self.id))
            self.notes = mann.get_all_where("notes",id=("=",self.id))

            self.cached[self.id]["values"] = list(self.values)
            self.cached[self.id]["tags"] = list(self.tags)
            self.cached[self.id]["notes"] = list(self.notes)
            
        # print "cached: ",self.cached[self.id]
    def add_header_label(self,header):
        """Add label for a header value"""
        strvar = tk.StringVar()
        strvar.set(header)
        lbl = tk.Label(self.replay_header,textvariable=strvar,relief=tk.RAISED,wraplength="300")
        col = self.headers.index(header)
        self.headervars.append(strvar)
        lbl.grid(row=0,column=col,sticky="NSWE")
        self.replay_header.grid_columnconfigure(col,weight=1)
        return lbl

    def init(self):
        """Construct self given values, self.headers need to be set so that associated data can be found."""
        self.load_values_from_db()
        self.populate_headers()
        self.table.configure(height=len(self.values) if len(self.values) > 2 else 4)
        self.make_table()
        
        self.taglist.delete(0,"end")
        for (_,tag,time) in self.tags:
            self.taglist.insert(tag,time)
        self.note_body.delete("1.0","end")
        #print self.notes
        self.note_body.insert("end",self.notes[0][1] if self.notes else "")


    def __init__(self,parent,**kw):
        self.headervars = []
        self.cached = {}
        self.cache_order = []
        self.headers = []
        self.use_headers(kw.pop("headers",[]))

        tk.Frame.__init__(self,parent,kw)
        
        self.mFont = tkFont.Font(family="Helvetica",size=14)
        #Make the top info: name,map,date
       

        #Table with tags on the side
        tableframe = tk.Frame(self)
        self.replay_header = tk.Frame(tableframe)
        self.table = ttk.Treeview(tableframe,selectmode="none")
        self.replay_header.grid(row=0,column=0,sticky="WNE")
        self.table.grid(row=1,column=0,sticky="N")
        tableframe.grid(row=0,column=0,sticky="N")
        #############################


        self.taglist = TagList(self)
        self.taglist.grid(row=0,column=1,rowspan=2,sticky="NSWE")

        self.note_frame = tk.Frame(self)
        scrollbar = tk.Scrollbar(self.note_frame)
        self.note_body= tk.Text(self.note_frame,height=4,width=30)
        scrollbar.config(command=self.note_body.yview)

        self.note_body.config(yscrollcommand=scrollbar.set)
        self.note_body.grid(row=0,column=0,sticky="NSWE")
        scrollbar.grid(row=0,column=1,sticky="NSE")
        self.note_frame.grid_columnconfigure(0,weight=1)
        self.note_frame.grid(row=2,column=0,columnspan=2,sticky="NSWE")
        if self.headers:
            self.init()
        self.grid_rowconfigure(2,weight=1)
        self.grid_columnconfigure(0,weight=1)


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

