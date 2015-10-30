#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from db_manager import *


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
