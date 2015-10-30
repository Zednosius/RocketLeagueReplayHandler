#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from db_manager import *

class ReplayManager(tk.Frame):
    def __init__(self,parent, **kw):
        tk.Frame.__init__(self, parent, **kw)

        with DB_Manager() as mann:
            replays = mann.get_all("replays")
        # print replays
        tk.Label(self,text="Replays").grid(row=0,column=0,sticky="NS")
        tk.Button(self,text="Filter").grid(row=2,column=0)
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


        self.info = ReplayInfoFrame(self,width=100,height=100)#tk.Frame(self,width=100,height=100)

        self.info.grid(row=1,column=1)

        Lb1.link(Lb2)
        Lb2.link(Lb1)

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(1,weight=1)

    def replay_displayinfo(self,variables):
        self.info.use_headers(list(variables))
        self.info.init()

        

class DragDropList(tk.Listbox):

    def __init__(self, parent, **kw):
        self.parent = parent
        tk.Listbox.__init__(self, parent, kw)
        
        self.bindtags((self, parent, "all"))
        self.bind('<ButtonPress-1>', self.set_current)
        self.bind('<ButtonRelease-1>', self.release)
        self.bind('<B1-Motion>',self.motion)
        self.bind('<Shift-B1-Motion>',self.motion_reverse)
        self.bind('<Double-ButtonPress-1>',self.notify_parent_displayinfo)
        self.bind('<space>',self.notify_parent_displayinfo)
        self.bind('<Up>',lambda e,di=-1:self.select_arrow(e,di))
        self.bind('<Down>',lambda e,di=1:self.select_arrow(e,di))
        self.bind('<Left>',lambda e:self.otherDropList.focus_set())
        self.bind('<Right>',lambda e:self.otherDropList.focus_set())
        self.bind('<Return>',self.enter_press)

        self.variables = []

    def link(self,otherDropList):
        self.otherDropList = otherDropList

    def select_arrow(self,event,di):
        selected = self.curselection()
        if len(selected) == 1:
            # print self.size()
            # print "mov to: ",(self.itemdown+di) % self.size()
            self.selection_set((self.itemdown+di) % self.size())
            self.selection_clear(self.itemdown)
            self.itemdown = (self.itemdown+di) % self.size()
        elif len(selected) == 0 and self.size() > 0:
            self.selection_set(0)
            self.itemdown = 0

    def notify_parent_displayinfo(self, event):
       
        if event.keysym == "??":
            item = self.nearest(event.y)
            # print "Clearing and reselecting"
            self.selection_clear(0,"end")
            self.selection_set(item)
        else:
            item = self.itemdown

        # print "Doubleclicked"
        resolved = False 
        parent = event.widget.winfo_parent()
        while not resolved and self.size() > 0:
            if parent =="":
                break
            else:
                print parent
            wid = self.nametowidget(parent)

            notify = getattr(wid,"replay_displayinfo",None)
            if callable(notify):
                resolved = True
                notify(self.variables[int(item)])
            parent = wid.winfo_parent()


    def set_current(self, event):
        """Selects an item"""
        self.focus_set()
        self.itemdown = self.nearest(event.y)
        self.itemdown_pre = self.selection_includes(self.itemdown)
        self.selection_set(self.itemdown)

    def selection_toggle(self, x,unselect=False,select=False):
        """Toggles an item between selected and unselected"""
        if self.selection_includes(x):
            self.selection_clear(x)
        else:
            self.selection_set(x)

        if unselect:
            self.selection_clear(x)
        if select:
            self.selection_set(x)

    def motion(self, event):
        """Either selects items that the user drags over or drops item into the other list"""
        if self.otherDropList and self.otherDropList.contains(event):
            self.motion_linked(event)
        elif self.contains(event):
            x = self.nearest(event.y)
            self.selection_set(x)
            self.focus_set()

    def motion_reverse(self,event):
        """When the user drags with shift hold it deselects dragged over items"""
        x = self.nearest(event.y)
        self.selection_clear(x)
        self.focus_set()

    def motion_linked(self,event):
        """If we enter the other list"""
        x = self.otherDropList.nearest(event.y_root-self.otherDropList.winfo_rooty())
        self.otherDropList.focus_set()
        self.otherDropList.activate(x)


    def release(self, event):
        """Releasing mousebutton inside the linked list transfers the items.
           If it was inside the same list and it was over the same item it gets toggled.
        """
        if self.otherDropList and self.otherDropList.contains(event):
            self.release_linked(event)
        elif self.itemdown == self.nearest(event.y) and self.itemdown_pre == 1:
            x = self.selection_includes(self.nearest(event.y))
            self.selection_clear(0,"end")
            self.selection_toggle(self.nearest(event.y),unselect=x)


    def insert(self,idx,text,variables):
        tk.Listbox.insert(self,idx,text)
        self.variables.insert(self.size(),variables)
        # print self.variables

        

    def release_linked(self, event):
        """Called when mousebutton released over the linked list.
            Removes items from the first list and adds them to the other
        """
        # print self.curselection()
        ot = self.otherDropList
        #Go backwards so as to not delete wrong item when the list resizes
        l = self.curselection()

        items = []
        varl = []
        for d in reversed(l):
            # print d,type(d)
            items.append( self.get(d) )
            varl.append( self.variables[int(d)] )
            self.delete(d)
            self.variables.pop(int(d))

        # print items
        y = event.y_root-ot.winfo_rooty()
        i = ot.nearest(y)

        for item in reversed(items):
            if ot.nearest(y) == -1:
                ot.insert("end",item,varl.pop())
                i = ot.nearest(y)
                continue
            
            # print i
            bbox = ot.bbox(i)
            if bbox==None or bbox[3]/2.0 > y: 
                ot.insert(i,item,varl.pop())
            else:
                ot.insert(i+1,item,varl.pop())
            i += 1

        # print "me",self.variables
        # print "other",self.otherDropList.variables

    def enter_press(self,event):
        self.release_linked(event)
        if not hasattr(self,'itemdown'): return

        if self.size() == 0:
            return
        if self.size()-1 < self.itemdown:
            self.selection_set(self.itemdown-1)
            self.itemdown = self.itemdown-1
        else:
            self.selection_set(self.itemdown)
            print "select, ",self.itemdown

    def contains(self,event):
        """Check if an event took place inside the container"""
        return event.x_root > self.winfo_rootx() \
                and event.x_root < self.winfo_rootx()+self.winfo_width() \
                and event.y_root > self.winfo_rooty() \
                and event.y_root < self.winfo_rooty()+self.winfo_height()


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
        self.mFont = kw.pop("mFont")
        tk.Frame.__init__(self,parent,kw)
        
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.tag_body = tk.Listbox(self, background="#F0F8FF",font=self.mFont, width=10,yscrollcommand=self.scrollbar.set)
        self.tag_body.bind("<MouseWheel>",lambda event : self.tag_body.yview("scroll",-event.delta/120,"units"))
        self.scrollbar.config(command=self.tag_body.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tag_body.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        

    def insert(self,tagname,timestamp):
        self.tag_body.insert("end",tagname+"@"+timestamp)
        self.tag_body.config(width=0)
    def delete(self,index,end):
        self.tag_body.delete(index,end)

class ReplayInfoFrame(tk.Frame):

    def motion(self,event):

        return "break"

    def make_table(self):
        
        self.table.bind_class(self.table,"<B1-Motion>",self.motion)


        self.allcols = ["#1","#2","#3","#4"]
        self.table["columns"] =["#1","#2","#3","#4"]
        style = ttk.Style(self)
        style.configure('Treeview', rowheight=40)

        #Set up headings
        self.table.heading("#1", text="Player",command=lambda:treeview_sort_column(self.table, "#1", False,str))
        self.table.heading("#2", text="Team",command=lambda:treeview_sort_column(self.table , "#2", False,int))
        self.table.heading("#3", text="Goals",command=lambda:treeview_sort_column(self.table, "#3", False,int))
        self.table.heading("#4", text="Saves",command=lambda:treeview_sort_column(self.table, "#4", False,int))
       
        #Remove the first column
        self.table.column("#0",width=0,minwidth=0)
        self.table_insert_values()
        
    def table_insert_values(self):
        """Inserts all values in self.values into the table"""
        self.table.delete(*self.table.get_children())
        for col in self.allcols:
            self.table.column(col,anchor='center',minwidth=50,width=60)
        f = lambda vals : val
        for values in self.values:
            self.table.insert("", "end",
             values=values[1:],
             tags=("red" if int(values[2]) == 1 else "blue"))

            if(self.table.column("#1","width") < self.mFont.measure(values[1])): #Adjust table column size if needed
                self.table.column("#1",width=int(self.mFont.measure(values[1])*1.2))


        self.table.tag_configure('red' , background='#FF6A6A',font=self.mFont)
        self.table.tag_configure('blue', background='#82CFFD',font=self.mFont)

    def populate_headers(self):
        """Inserts all header texts from self.headers"""
        added = False
        for i in range(0,len(self.headers)):
            # print "headr: ",self.headers[i]
            if(len(self.headervars) > i):
                # print "replacing header ",self.headervars[i],"with",self.headers[i]
                self.headervars[i].set(self.headers[i])
            else:
                # print "added headerlabel", len(self.headervars)
                lbl = self.add_header_label(self.headers[i])
                added = True
        if added:
            lbl.grid(stick="WNSE")        
        


    def use_headers(self,headers):
        """Uses the headers provided, replacing the old ones"""
        self.headers = headers
        if headers:  
            self.id = self.headers.pop(0)
            self.filename = self.headers.pop(0)
            if(len(self.headervars) == len(self.headers)):
                self.populate_headers()

    def load_values_from_db(self):
        """Load data from database"""
        with DB_Manager() as mann:
            self.values = mann.get_all_where("teams",id=("=",self.id))
            self.tags = mann.get_all_where("tags",id=("=",self.id))
            self.notes = mann.get_all_where("notes",id=("=",self.id))

    def add_header_label(self,header):
        """Add label for a header value"""
        strvar = tk.StringVar()
        strvar.set(header)
        lbl = tk.Label(self.replay_header,font=self.mFont,textvariable=strvar,relief=tk.RAISED,wraplength="300")
        col = self.headers.index(header)
        self.headervars.append(strvar)
        lbl.grid(row=0,column=col,sticky="NS")
        self.replay_header.colnum=col
        return lbl

    def init(self):
        """Construct self given values, self.headers need to be set so that associated data can be found."""
        self.load_values_from_db()
        self.populate_headers()
        self.replay_header.grid_columnconfigure(self.replay_header.colnum,weight=1)
        self.make_table()
        self.table.configure(height=len(self.values))
        self.taglist.delete(0,"end")
        for (_,tag,time) in self.tags:
            self.taglist.insert(tag,time)


    def __init__(self,parent,**kw):
        self.headervars = []

        self.use_headers(kw.pop("headers",[]))

        tk.Frame.__init__(self,parent,kw)
        
        self.mFont = tkFont.Font(family="Helvetica",size=14)
        #Make the top info: name,map,date
        self.replay_header =tk.Frame(self)

        self.replay_header.grid(sticky="WE")

        self.table = ttk.Treeview(self,selectmode="none")

        if self.headers:
            self.init()
            
        
        self.taglist = TagList(self,mFont=self.mFont)

        self.taglist.grid(row=1,column=2,sticky="NS")
        self.note_body = tk.Frame(self)

        self.replay_header.grid(row=0,column=0,columnspan=3)

        self.table.grid(        row=1,column=0,columnspan=2,sticky="NS")

        self.note_body.grid(    row=2,column=0,columnspan=3)


        

