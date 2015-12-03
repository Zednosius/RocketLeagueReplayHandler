#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import Tkinter as tk



class Entry(tk.Entry):
    def __init__(self,parent=None,**kw):
        tk.Entry.__init__(self,parent,**kw)
        self.bind("<Control-a>", self.ctrl_a)
    def ctrl_a(self,event):
        self.select_all_text()
        return "break"
    def select_all_text(self):
        self.select_range(0,tk.END)