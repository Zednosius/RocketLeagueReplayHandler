#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
from Tkinter import *
import ttk
import gui.CustomTkinter as cst

def output():
    print "Not implemented"
root = Tk()


menu = Menu(root)
root.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=output)
filemenu.add_command(label="Open...", command=output)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=output)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=output)

cst.ReplayManager(root).pack(expand=True,fill=BOTH)

root.mainloop()
