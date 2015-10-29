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
        print replays

        Lb1 = DragDropList(self)
        for replay in replays:
            Lb1.insert("end",replay[1],replay)
        Lb1.grid(row=0,column=0,sticky="NSWE")

        Lb2 = DragDropList(self)
        Lb2.grid(row=0,column=2,sticky="NSWE")

        self.info = tk.Frame(self,width=100,height=100)#ReplayInfoFrame(self,headers=["MyReplay","Utopia Stadium","2015-03-12:22-22"],bg="orange")

        # info.pack(fill="x",anchor="n")
        self.info.grid(row=0,column=1)

        Lb1.link(Lb2)
        Lb2.link(Lb1)

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(0,weight=1)

    def replay_doubleclicked(self,variables):
        self.info.grid_forget()
        self.info = ReplayInfoFrame(self,headers=list(variables),bg="orange")
        self.info.grid(row=0,column=1)
        

class DragDropList(tk.Listbox):

    def __init__(self, parent, **kw):
        self.parent = parent
        tk.Listbox.__init__(self, parent, kw)
        
        self.bindtags((self, parent, "all"))
        self.bind('<ButtonPress-1>', self.set_current)
        self.bind('<ButtonRelease-1>', self.release)
        self.bind('<B1-Motion>',self.motion)
        self.bind('<Shift-B1-Motion>',self.motion_reverse)
        self.bind('<Double-ButtonPress-1>',self.notify_parent_doubleclick)
        self.variables = []

    def link(self,otherDropList):
        self.otherDropList = otherDropList

    def notify_parent_doubleclick(self,event):
        item = self.nearest(event.y)
        resolved = False 
        while not resolved:
            parent = event.widget.winfo_parent()
            if parent =="":
                break
            else:
                print parent
            wid = self.nametowidget(parent)

            notify = getattr(wid,"replay_doubleclicked",None)
            if callable(notify):
                resolved = True
                notify(self.variables[int(item)])


    def set_current(self, event):
        """Selects an item"""
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
        print self.variables

        

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
            print d,type(d)
            items.append( self.get(d) )
            varl.append( self.variables[int(d)] )
            self.delete(d)
            self.variables.pop(int(d))

        print items

        for item in reversed(items):

            y = event.y_root-ot.winfo_rooty()

            if ot.nearest(y) == -1:
                ot.insert("end",item,varl.pop())
                continue
            i = ot.nearest(y)
            # print i
            bbox = ot.bbox(i)
            if bbox==None or bbox[3]/2.0 > y: 
                ot.insert(i,item,varl.pop())
            else:
                ot.insert(i+1,item,varl.pop())

        print "me",self.variables
        print "other",self.otherDropList.variables

    def contains(self,event):
        """Check if an event took place inside the container"""
        return event.x_root > self.winfo_rootx() \
                and event.x_root < self.winfo_rootx()+self.winfo_width() \
                and event.y_root > self.winfo_rooty() \
                and event.y_root < self.winfo_rooty()+self.winfo_height()


#http://stackoverflow.com/questions/1966929/tk-treeview-column-sort
def treeview_sort_column(tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
                   treeview_sort_column(tv, col, not reverse))


class TagList(tk.Frame):
    def __init__(self,parent,**kw):
        self.mFont = kw.pop("mFont")
        tk.Frame.__init__(self,parent,kw)
        
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.tag_body = tk.Listbox(self, background="#F0F8FF",font=self.mFont, width=10,yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tag_body.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tag_body.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.insert("save","2:22")
        self.insert("AMAZING","2:22")
        

    def insert(self,tagname,timestamp):
        self.tag_body.insert("end",tagname+"@"+timestamp)
        self.tag_body.config(width=0)

class ReplayInfoFrame(tk.Frame):

    def motion(self,event):

        return "break"

    def make_table(self):
        self.table = ttk.Treeview(self,selectmode="none",height=6)
        
        self.table.bind_class(self.table,"<B1-Motion>",self.motion)


        self.allcols = ["#1","#2","#3","#4"]
        self.table["columns"] =["#1","#2","#3","#4"]
        style = ttk.Style(self)
        style.configure('Treeview', rowheight=40)

        #Set up headings
        self.table.heading("#1", text="Player",command=lambda:treeview_sort_column(self.table, "#1", False))
        self.table.heading("#2", text="Team",command=lambda:treeview_sort_column(self.table , "#2", False))
        self.table.heading("#3", text="Goals",command=lambda:treeview_sort_column(self.table, "#3", False))
        self.table.heading("#4", text="Saves",command=lambda:treeview_sort_column(self.table, "#4", False))
       
        #Remove the first column
        self.table.column("#0",width=0,minwidth=0)

        for col in self.allcols:
            self.table.column(col,anchor='center',minwidth=50,width=60)

        for values in self.values:
            self.table.insert("", "end",
             values=values,
             tags=("red" if values[0] == 1 else "blue"))

            if(self.table.column("#1","width") < self.mFont.measure(values[0])): #Adjust table column size if needed
                self.table.column("#1",width=int(self.mFont.measure(values[0])*1.2))


        self.table.tag_configure('red' , background='#FF6A6A',font=self.mFont)
        self.table.tag_configure('blue', background='#82CFFD',font=self.mFont)


    def __init__(self,parent,**kw):
        self.headers = kw.pop("headers",[])
        self.values = kw.pop("value",[])
        self.id = self.headers.pop(0)
        self.filename = self.headers.pop(0)
        
        tk.Frame.__init__(self,parent,kw)
        
        self.mFont = tkFont.Font(family="Helvetica",size=14)


        with DB_Manager() as mann:
            teams = mann.get_all_where("teams",id=("=",self.id))


        #Make the top info: name,map,date
        self.replay_header =tk.Frame(self, background="red")
        self.replay_header.grid(sticky="WE")
        for header in self.headers:
            lbl = tk.Label(self.replay_header,font=self.mFont,text=header,relief=tk.RAISED,wraplength="300")
            col = self.headers.index(header)
            lbl.grid(row=0,column=col,sticky="NS")
        lbl.grid(stick="WNSE")
        self.replay_header.grid_columnconfigure(col,weight=1)
        self.make_table()


        #Create the body for tags
        self.taglist = TagList(self,mFont=self.mFont)
        self.taglist.grid(row=1,column=2,sticky="NS")
        self.note_body =tk.Frame(self, background="red")

        self.replay_header.grid(row=0,column=0,columnspan=3)

        self.table.grid(        row=1,column=0,columnspan=2)

        self.note_body.grid(    row=2,column=0,columnspan=3)

