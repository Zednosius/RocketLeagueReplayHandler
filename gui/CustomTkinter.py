#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

from Tkinter import *
import ttk
import tkFont
print "Tcl:",TclVersion 
print "Tkv:",TkVersion
class ReplayManager:
    def __init__(self,parent):
        pass


class DragDropList(Listbox):
    def __init__(self, parent, **kw):
        
        Listbox.__init__(self, parent, kw)
        
        self.bindtags((self, parent, "all"))
        self.bind('<ButtonPress-1>', self.set_current)
        self.bind('<ButtonRelease-1>', self.release)
        self.bind('<B1-Motion>',self.motion)
        self.bind('<Shift-B1-Motion>',self.motion_reverse)


    def link(self,otherDropList):
        self.otherDropList = otherDropList

    def set_current(self, event):
        """Selects an item"""
        self.itemdown = self.nearest(event.y)
        self.itemdown_pre = self.selection_includes(self.itemdown)
        self.selection_set(self.itemdown)

    def selection_toggle(self, x):
        """Toggles an item between selected and unselected"""
        if self.selection_includes(x):
            self.selection_clear(x)
        else:
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
            self.selection_toggle(self.nearest(event.y))

       
        

    def release_linked(self, event):
        """Called when mousebutton released over the linked list.
            Removes items from the first list and adds them to the other
        """
        print self.curselection()
        ot = self.otherDropList
        #Go backwards so as to not delete wrong item when the list resizes
        for d in reversed(self.curselection()):
            item = self.get(d)
            self.delete(d)
            y = event.y_root-ot.winfo_rooty()
            i = ot.nearest(y)

            if ot.bbox(i)[3]/2.0 > y: 
                ot.insert(i,item)
            else:
                ot.insert(i+1,item)

    def contains(self,event):
        """Check if an event took place inside the container"""
        return event.x_root > self.winfo_rootx() \
                and event.x_root < self.winfo_rootx()+self.winfo_width() \
                and event.y_root > self.winfo_rooty() \
                and event.y_root < self.winfo_rooty()+self.winfo_height()

class Table(Frame):
    def __init__(self,parent,**kw):
        Frame.__init__(self,parent,kw)
        self.headers = kw.pop("headers")
        self.header_list = []
        self.rows = 1
        self.columns = len(self.headers)
        for header in self.headers:
            lbl = Label(self, text=header)
            lbl.grid(row = self.rows, column=self.headers.index(header))
            header_list.append(lbl)
        self.grid_columnconfigure

    def insert(self,row,values):
        pass





class ReplayInfoFrame(Frame):

    def drag(self,event):
        pass

    def treepress(self,event):
        self.pressed_column = self.team_body.identify("column",event.x,event.y)
        print "pressed: "+self.pressed_column
        self.px = event.x
        self.py = event.y

    def __init__(self,parent,**kw):
        Frame.__init__(self,parent,kw)
        
        mFont = tkFont.Font(family="Helvetica",size=14,weight=tkFont.BOLD)

        self.replay_header = Frame(self, background="red")
        ttk.Label(self.replay_header,font=mFont, text="Name").grid(row=0, column=0,sticky="W")
        Label(self.replay_header,font=mFont, text="Map").grid(row=0, column=1)
        Label(self.replay_header,font=mFont, text="Score").grid(row=0, column=2)
        Label(self.replay_header,font=mFont, text="Hello World!").grid(row=0, column=3,sticky="E")

        for i in range(0,4):
            self.replay_header.grid_columnconfigure(i,weight=1)

        self.team_body = ttk.Treeview(self)
        self.team_body.bind("<B1-Motion>",self.drag)
        self.team_body.bind("<ButtonPress-1>",self.treepress)
        #self.team_body.bindtags((self.team_body, self, "all"))
        #self.team_body.bind("<<TreeviewResizeDrag>>",self.drag)
        self.team_body.bind("<<TreeviewSelect>>",self.drag)

        #self.team_body['show'] = 'headings'
        self.team_body["columns"] =["#1","#2","#3"]

        self.team_body.heading("#0", text="Player")
        self.team_body.heading("#1", text="Team")
        self.team_body.heading("#2", text="Goals")
        self.team_body.heading("#3", text="Saves")


        self.team_body.column("#0",anchor='center',minwidth=50)
        self.team_body.column("#1",anchor='center',minwidth=50)
        self.team_body.column("#2",anchor='center',minwidth=50)
        self.team_body.column("#3",anchor='center',minwidth=50)
        # Label(self.team_body,text="Blue Team", font=mFont, fg="Blue", bg="white").grid(row=0, column=0)
        # Label(self.team_body,text="Red Team" , font=mFont, fg="Red", bg="white").grid(row=0, column=2)
        # Frame(self.team_body,background="black",height=1).grid(row=1,columnspan=3,sticky="WE")
        # Frame(self.team_body,background="black",width=1).grid(row=0,column=1,rowspan=5,sticky="SN")
        #for i in range(1,4):
        #Label(self.team_body,text="Player "+str(i), font=mFont, fg="Blue").grid(row=i+1, column=0)
        #Label(self.team_body,text="Player "+str(i+3), font=mFont, fg="Red").grid(row=i+1, column=2)
        for i in range(1,7):
            self.team_body.insert("", "end",text="Player "+str(i), values=(str(i%1),str(((i*4)**2)%5),str(((i*3)**2)%5)),tags=("even" if i%2==0 else "odd",))

        self.team_body.tag_configure('odd' , background='orange')
        self.team_body.tag_configure('even', background='purple')

        self.tag_body = Frame(self, background="green")
        self.note_body = Frame(self, background="red")
        self.replay_header.grid(row=0,sticky="WE")
        self.team_body.grid(row=1,sticky="WE")
        self.tag_body.grid(row=1,sticky="E")
        self.note_body.grid(row=2,sticky="S")


        print dir(self.team_body)
        t = self.team_body
        print t.slaves
        print t.location
        
        print t.config
        print t.children
        print t.get_children()
        print t._tclCommands

        for i in range(0,3):
            self.grid_columnconfigure(i,weight=1)
            self.grid_rowconfigure(i,weight=1)
        self.grid_columnconfigure(3,weight=1)