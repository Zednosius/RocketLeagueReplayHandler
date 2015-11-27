#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from Popups import *
from db_manager import *
import logging
import tasks
import copy

logger = logging.getLogger(__name__)
# logger.debug_ = logger.debug
# def dbg(txt,*args):
#     print txt % args
#     logger.debug_(txt,*args)

# logger.debug = dbg
def tag_popup(taglist, infowidget):
    if hasattr(infowidget,"id"):
        TagPopup(taglist=taglist,infowidget=infowidget)

def group_popup(grouplist,infowidget):
    if hasattr(infowidget,"id"):
        AddToGroupPopup(grouplist=grouplist, replay_id=infowidget.id, winfo_rootc=(infowidget.winfo_rootx(),infowidget.winfo_rooty()))

#http://stackoverflow.com/questions/1966929/tk-treeview-column-sort
def treeview_sort_column(tv, col, reverse, cast):
        l = [(cast(tv.set(k, col)), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
                   treeview_sort_column(tv, col, not reverse,cast))

class ReplayInfoFrame(tk.Frame):


    def make_table(self):

        self.allcols = ["#1","#2","#3","#4"]
        self.table["columns"] =["#1","#2","#3","#4"]
        style = ttk.Style(self)
        style.configure('Treeview', rowheight=40)
        self.table['show'] = 'headings'
        #Set up headings
        self.table.heading("#1", text="Player",command=lambda:treeview_sort_column(self.table, "#1", False,unicode))
        self.table.heading("#2", text="Team"  ,command=lambda:treeview_sort_column(self.table ,"#2", False,int))
        self.table.heading("#3", text="Goals" ,command=lambda:treeview_sort_column(self.table, "#3", False,int))
        self.table.heading("#4", text="Saves" ,command=lambda:treeview_sort_column(self.table, "#4", False,int))
        for col in self.allcols:
            self.table.column(col,anchor='center',minwidth=75,width=75,stretch=True)
        self.table.column("#1",anchor='center',minwidth=100,width=100,stretch=True)
        #Remove the first column
        self.table.column("#0",width=0,minwidth=0)
        # self.table_insert_values()
        logger.info("Made table")

    def table_insert_values(self):
        """Inserts all values in self.teams into the table"""
        self.table.delete(*self.table.get_children())
    
        for values in self.teams:
            self.table.insert("", "end",
             values=values[1:],
             tags=("orange" if int(values[2]) == 1 else "blue"))

            if(self.table.column("#1","width") < self.mFont.measure(values[1])): #Adjust table column size if needed
                self.table.column("#1",width=int(self.mFont.measure(values[1])*1.2))
                #print "Adjusted columnsize"
        

        self.table.tag_configure('orange' , background='#FF7F00',font=self.mFont)
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

    def clear(self):
        self.save()
        self.table.delete(*self.table.get_children())
        self.taglist.delete(0,"end")
        self.grouplist.delete(0,"end")
        self.note_body.delete("1.0","end")
        for headervar in self.headervars:
            headervar.set("")
        self.replay_entry = None
        self.headers = []
        self.teams = []
        logger.info("Cleared table")

    def save(self):
        #Save old notes
        if len(self.headers) != 0:
            tasks.start_task(self,None,tasks.save_data,{"id":self.id,"note":self.note_body.get("1.0","end-1c")})

    

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

    def display(self,displaydata):
        #Displaydata keys: headers, teams, tags, groups, notes
        # print "Displaying",displaydata
        self.displaydata = copy.deepcopy(displaydata)
        self.id = displaydata['headers'].pop(0)
        self.filename = displaydata['headers'].pop(0)
        self.headers = displaydata['headers']
        self.teams = displaydata['teams']
        self.populate_headers()
        self.make_table()
        self.table_insert_values()

        for (_,tag,time) in displaydata['tags']:
            self.taglist.insert(tag,time)
            logger.debug("Inserted tag %s@%s",tag,time)


        for group in displaydata['groups']:
            if type(group) == tuple:
                group = group[0]
            self.grouplist.insert(group)
            logger.debug("Inserted group %s",group)

        self.note_body.insert("end",displaydata['notes'][0][1] if displaydata['notes'] else "")
        logger.info("Initialization complete")

    def __init__(self,parent,**kw):
        self.headervars = []
        self.headers = []
        tk.Frame.__init__(self,parent,kw)
        
        self.mFont = tkFont.Font(family="Helvetica",size=14)
       

        #Table with tags on the side
        tableframe = tk.Frame(self)
        self.replay_header = tk.Frame(tableframe)
        self.table = ttk.Treeview(tableframe,selectmode="none")
        self.replay_header.grid(row=0,column=0,sticky="WNE")
        self.table.grid(row=1,column=0,sticky="N")
        tableframe.grid(row=0,column=0,sticky="N")
        self.make_table()
        #############################


        self.taglist = TagList(self,callback=tag_popup,text="Add tag")
        self.taglist.grid(row=0,column=1,rowspan=2,sticky="NSWE")

        self.grouplist = GroupList(self,callback=group_popup,text="Add group")
        self.grouplist.grid(row=0,column=2,rowspan=2,sticky="NSWE")

        self.note_frame = tk.Frame(self)
        scrollbar = ttk.Scrollbar(self.note_frame)
        self.note_body= tk.Text(self.note_frame,height=4,width=30,maxundo=15,undo=15)
        self.note_body.bind("<Control-A>", lambda e: self.note_select_all())
        self.note_body.bind("<Control-a>", lambda e: self.note_select_all())
        scrollbar.config(command=self.note_body.yview)

        self.note_body.config(yscrollcommand=scrollbar.set)
        self.note_body.grid(row=0,column=0,sticky="NSWE")
        scrollbar.grid(row=0,column=1,sticky="NSE")
        self.note_frame.grid_columnconfigure(0,weight=1)
        self.note_frame.grid(row=2,column=0,columnspan=3,sticky="NSWE")

        if self.headers:
            self.init()
        self.grid_rowconfigure(2,weight=1)
        self.grid_columnconfigure(0,weight=1)


    def note_select_all(self):
        self.note_body.tag_add("sel","1.0","end-1c")
        return "break"

class TagList(tk.Frame):
    def __init__(self,parent,**kw):
        self.mFont = kw.pop("mFont",tkFont.nametofont("TkDefaultFont"))
        self.callback = kw.pop("callback",None)
        self.add_text = kw.pop("text","Add")
        self.list = []
        tk.Frame.__init__(self,parent,kw)
        
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.list_body = tk.Listbox(self, background="#F0F8FF",font=self.mFont, width=10,yscrollcommand=self.scrollbar.set)
        self.list_body.bind("<MouseWheel>",lambda event : self.list_body.yview("scroll",-event.delta/120,"units"))
        self.scrollbar.config(command=self.list_body.yview)
        self.addbutton = ttk.Button(self,text=self.add_text,command=lambda taglist=self,parent=parent : self.callback(taglist,parent))

        self.addbutton.grid(row=1,columnspan=2,stick="WE")#.pack(side=tk.BOTTOM,fill=tk.X,expand=1)
        self.scrollbar.grid(row=0,column=1,sticky="SN")#.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_body.grid(row=0,column=0,sticky="NSWE")#.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.grid_rowconfigure(0,weight=1)

    def insert(self,tagname,timestamp):
        
        self.list.append((tagname,timestamp))
        self.list_body.insert("end",str(tagname)+" @ "+str(timestamp))
        self.list_body.config(width=0)
    
    def see(self,index):
        self.list_body.see(index)

    def delete(self,index,end):
        self.list = self.list[0:index]+self.list[len(self.list) if end =="end" else end:len(self.list)]
        self.list_body.delete(index,end)

class GroupList(TagList):

    def insert(self,groupname):
        self.list.append(groupname)
        self.list_body.insert("end",groupname)

