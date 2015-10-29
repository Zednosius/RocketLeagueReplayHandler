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
            self.selection_clear(0,END)
            self.selection_toggle(self.nearest(event.y),unselect=x)


       
        

    def release_linked(self, event):
        """Called when mousebutton released over the linked list.
            Removes items from the first list and adds them to the other
        """
        # print self.curselection()
        ot = self.otherDropList
        #Go backwards so as to not delete wrong item when the list resizes
        l = self.curselection()
        it = []
        for d in reversed(l):
            it.append( self.get(d) )
            self.delete(d)
        for item in reversed(it):

            y = event.y_root-ot.winfo_rooty()
            if ot.nearest(y) == -1:
                ot.insert(END,item)
                continue

            i = ot.nearest(y)
            # print i
            bbox = ot.bbox(i)
            if bbox==None or bbox[3]/2.0 > y: 
                ot.insert(i,item)
            else:
                ot.insert(i+1,item)

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


class TagList(Frame):
    def __init__(self,parent,**kw):
        self.mFont = kw.pop("mFont")
        Frame.__init__(self,parent,kw)
        
        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.tag_body = Listbox(self, background="#F0F8FF",font=self.mFont, width=10,yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tag_body.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.tag_body.pack(side=LEFT, fill=BOTH, expand=1)
        self.insert("save","2:22")
        self.insert("AMAZING","2:22")
        

    def insert(self,tagname,timestamp):
        self.tag_body.insert(END,tagname+"@"+timestamp)
        self.tag_body.config(width=0)

class ReplayInfoFrame(Frame):

    def motion(self,event):

        return "break"

    def make_table(self):
        self.table = ttk.Treeview(self,selectmode="none",height=6)

        for item in self.table.keys():
            print(item),(self.table.cget(item))
        
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
       
        self.table.column("#0",width=0,minwidth=0)
        for col in self.allcols:
            self.table.column(col,anchor='center',minwidth=50,width=60)

        for i in range(1,7):
            self.table.insert("", "end",
             values=("Player "+str(i),"Red" if i%2 == 1 else "Blue",str(((i*4)**2)%5),str(((i*3)**2)%5)),
             tags=("even" if i%2==0 else "odd","red" if i%2 == 1 else "blue"))
            if(self.table.column("#1","width") < self.mFont.measure("Player "+str(i))):
                print "size bf: ",self.table.column("#1","width")
                print "font msz: ",self.mFont.measure("Player "+str(i))
                self.table.column("#1",width=int(self.mFont.measure("Player "+str(i))*1.2))

            print "red" if i%2 == 1 else "blue"

        self.table.tag_configure('red' , background='#FF6A6A',font=self.mFont)
        self.table.tag_configure('blue', background='#82CFFD',font=self.mFont)


    def __init__(self,parent,**kw):
        self.headers = kw.pop("headers",[])
        self.values = kw.pop("value",[])

        
        Frame.__init__(self,parent,kw)
        
        self.mFont = tkFont.Font(family="Helvetica",size=14)

        #Make the top info: name,map,date
        self.replay_header = Frame(self, background="red")
        self.replay_header.grid(sticky="WE")
        for header in self.headers:
            lbl = Label(self.replay_header,font=self.mFont,text=header,relief=RAISED,wraplength="300")
            col = self.headers.index(header)
            lbl.grid(row=0,column=col,sticky="NS")
        lbl.grid(stick="WNSE")
        self.replay_header.grid_columnconfigure(col,weight=1)
        self.make_table()


        #Create the body for tags
        self.taglist = TagList(self,mFont=self.mFont)
        self.taglist.grid(row=1,column=2,sticky="NS")
        self.note_body = Frame(self, background="red")

        self.replay_header.grid(row=0,column=0,columnspan=3)

        self.table.grid(        row=1,column=0,columnspan=2)

        self.note_body.grid(    row=2,column=0,columnspan=3)

