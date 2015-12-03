#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import Tkinter as tk

def recursive_widget_bind(widget,binding,bind_func):
    """
    Binds bind_func with binding to widget and all of its descendants. Useful for when you want a semi-wide application binding. 
    Eg. want binding in main application but not popup windows.
    """
    widget.bind(binding,bind_func)
    for child in widget.winfo_children():
        recursive_widget_bind(child,binding,bind_func)

class Entry(tk.Entry):
    def __init__(self,parent=None,**kw):
        tk.Entry.__init__(self,parent,**kw)
        self.bind("<Control-a>", self.ctrl_a)
    def ctrl_a(self,event):
        self.select_all_text()
        return "break"
    def select_all_text(self):
        self.select_range(0,tk.END)