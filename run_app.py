#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
from Tkinter import *
import ttk
import gui.HandlerApplication as cst
import sys
import os
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def output():
    print "Not implemented"

def on_exit():
    rman.save()
    root.destroy()
if not os.path.isfile(__location__+"\\rocketleague.db"):
    import setup
    setup.initdb()

root = Tk()
root.title("Rocket League Replay Handler")
root.minsize(700,500)
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

rman = cst.ReplayManager(root)
rman.pack(expand=True,fill=BOTH)
root.protocol("WM_DELETE_WINDOW",on_exit)
root.mainloop()
