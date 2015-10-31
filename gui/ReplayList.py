#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from db_manager import *


class ReplayList(tk.Listbox):

    def __init__(self, parent, **kw):
        self.parent = parent
        tk.Listbox.__init__(self, parent, kw)

        self.bind('<space>',self.notify_parent_displayinfo)
        self.bind('<ButtonPress-1>', self.show_clicked)
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
            self.selection_set((self.selected_item+di) % self.size())
            self.selection_clear(self.selected_item)
            self.selected_item = (self.selected_item+di) % self.size()
        elif len(selected) == 0 and self.size() > 0:
            self.selection_set(0)
            self.selected_item = 0

    def notify_parent_displayinfo(self, event):
        if not self.curselection():return
        print self.curselection()
        resolved = False 
        parent = event.widget.winfo_parent()
        self.selected_item = self.curselection()[0]
        while not resolved and self.size() > 0:
            if parent =="":
                break
            # else:
            #     print parent
            wid = self.nametowidget(parent)

            notify = getattr(wid,"replay_displayinfo",None)
            if callable(notify):
                resolved = True
                notify(self.variables[int(self.selected_item)])
            parent = wid.winfo_parent()

    def transfer_selection(self):
        if not hasattr(self,"otherDropList"):return
        l = self.curselection()
        items = []
        variables = []
        ##Remove from this list
        for d in reversed(l):
            items.append( self.get(d) )
            variables.append( self.variables[int(d)] )
        other = self.otherDropList

        while len(items) > 0:
            other.insert("end",items.pop(),variables.pop())

    def show_clicked(self,event):
        self.selected_item = self.nearest(event.y)
        self.notify_parent_displayinfo(event)

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

    def insert(self,idx,text,variables):
        tk.Listbox.insert(self,idx,text)
        self.variables.insert(self.size(),variables)
        # print self.variables
    def get_variables(self,index):
        return self.variables[index]
    def enter_press(self,event):
        if not hasattr(self,'selected_item'): return
        self.transfer_selection()

    def contains(self,event):
        """Check if an event took place inside the container"""
        return event.x_root > self.winfo_rootx() \
                and event.x_root < self.winfo_rootx()+self.winfo_width() \
                and event.y_root > self.winfo_rooty() \
                and event.y_root < self.winfo_rooty()+self.winfo_height()
