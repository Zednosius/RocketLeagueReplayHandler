#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
import Tkinter as tk
import ttk
import tkFont
from db_manager import *
import logging
logger = logging.getLogger(__name__)
print logger

class ReplayList(tk.Listbox):

    def __init__(self, parent, **kw):
        logger.info("Making replay list")
        self.parent = parent
        tk.Listbox.__init__(self, parent, kw)
        self.insert_callback = None
        self.delete_callback = None
        self.bind('<space>',self.notify_parent_displayinfo)
        self.bind('<ButtonPress-1>', self.click)

        self.bind('<Up>',lambda e,di=-1:self.select_arrow(e,di))
        self.bind('<Down>',lambda e,di=1:self.select_arrow(e,di))
        self.bind('<Left>',self.focus_other)
        self.bind('<Right>',self.focus_other)
        self.bind('<Return>',self.enter_press)

        self.bind('<<ListboxSelect>>',self.notify_parent_displayinfo)
        self.variables = []
        logger.info("Replay list made")

    def link(self,otherDropList):
        self.otherDropList = otherDropList
        logger.info("Linked with other list")

    def focus_other(self,e):
        if not hasattr(self,"otherDropList"): 
            return
        else:
            self.otherDropList.focus_set()

    def click(self,event):
        self.selected_item = self.nearest(event.y)

    def select_arrow(self,event,di):
        selected = self.curselection()
        if len(selected) == 1:
            logger.debug("Clearing selection %s",self.selected_item)
            self.selection_clear(self.selected_item)
            self.selected_item = (self.selected_item+di) % self.size()
            logger.debug("Selecting: %s",self.selected_item)
            self.selection_set(self.selected_item)
            self.see(self.selected_item)
            logger.debug("Scrolled to item")

        elif len(selected) == 0 and self.size() > 0:
            self.selection_set(0)
            self.selected_item = 0
            logger.debug("None selected, selecting first item")
        return "break"

    def notify_parent_displayinfo(self, event, useSelection=False):
        if not self.curselection():return "break"
        logger.info("Notifying parent of clicked replay")
        # print "Notify_Parent_DisplayInfo"
        resolved = False 
        parent = self.winfo_parent()
        if useSelection:
            self.selected_item = int(self.curselection()[0])
        
        while not resolved and self.size() > 0:
            if parent =="":
                return "break"
            wid = self.nametowidget(parent)

            notify = getattr(wid,"replay_displayinfo",None)
            if callable(notify):
                resolved = True
                logger.debug("Calling notify with : %s",self.variables[self.selected_item])
                notify(self.variables[self.selected_item])
            parent = wid.winfo_parent()
        return "break"

    def transfer_selection(self):
        if not hasattr(self,"otherDropList"):return
        l = self.curselection()
        items = []
        variables = []
        logger.info("Transferring items to other list")
        ##Remove from this list
        for d in reversed(l):
            items.append( self.get(d) )
            variables.append( self.variables[int(d)] )
        other = self.otherDropList
        while len(items) > 0:
            logger.debug("Inserting %s : %s",items[0],variables[0])
            for i,v in enumerate(other.variables if other.variables else [("",)*8]):
                #If the exact same item is already in the list we can skip it.
                if v[4] == variables[0][4] and v[0] == variables[0][0]:
                    items.pop()
                    variables.pop()
                    break
                elif v[4] < variables[0][4]:
                    other.insert(i,items.pop(),variables.pop())
                    break
                elif i+1 == len(other.variables):
                    other.insert("end",items.pop(),variables.pop())
                    break
            logger.debug("Insert done")
        logger.info("Transfer done")

    def show_clicked(self,event):
        self.selected_item = self.nearest(event.y)
        self.notify_parent_displayinfo(event,False)

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
        if self.insert_callback:
            self.insert_callback(variables)

        tk.Listbox.insert(self,idx,text)
        if idx == "end":
            logger.debug("Appending %s",variables)
            self.variables.append(variables)
        else:
            logger.debug("Inserting at %s with %s",idx,variables)
            self.variables.insert(idx,variables)
        # print self.variables

    def set_insert_callback(self,callback):
        self.insert_callback = callback

    def set_delete_callback(self,callback):
        self.delete_callback = callback

    def get_variables(self,index):
        return self.variables[index]

    def delete(self,start,end=None):
        tk.Listbox.delete(self,start,end)
        if self.delete_callback:
            varl = self.variables[start:end if end != None else start+1]
            logger.debug("Calling delete callback with %s",varl)
            self.delete_callback(varl)

        if not end:
            logger.debug("Removed variables %s at %s",self.variables[start], start)
            self.variables.pop(start)
        else:
            for i in range(end,start,-1):
                logger.debug("Removed variables %s at %s",self.variables[i-1],i-1)
                self.variables.pop(i-1)

    def delete_selected(self):
        # tk.Listbox.delete(self,self.selected_item)
        # logger.debug("Deleting selected variables %s",self.variables[self.selected_item])
        # self.variables.pop(self.selected_item)
        self.delete(self.selected_item)
        
        if self.selected_item >= self.size():
            self.selected_item -= 1

        self.selection_set(self.selected_item)
        self.notify_parent_displayinfo(None)

    def enter_press(self,event):
        if not hasattr(self,'selected_item'): return
        if hasattr(self,"otherDropList"): self.transfer_selection()
        else: self.notify_parent_displayinfo(event)

    def contains(self,event):
        """Check if an event took place inside the container"""
        return event.x_root > self.winfo_rootx() \
                and event.x_root < self.winfo_rootx()+self.winfo_width() \
                and event.y_root > self.winfo_rooty() \
                and event.y_root < self.winfo_rooty()+self.winfo_height()
