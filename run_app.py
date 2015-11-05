#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
from Tkinter import *
import ttk
import gui.HandlerApplication as cst
import sys
import os
import rl_paths
import shutil
import imp



def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])

def output():
    print "Not implemented"

def on_exit(rman,root):
    rman.save()
    root.destroy()

def restore():
    for f in os.listdir(rl_paths.backup_folder()):
        f = os.path.splitext(f)[0]
        shutil.move(rl_paths.backup_folder(f),rl_paths.demo_folder(f))

    shutil.rmtree(rl_paths.tracked_folder())
    shutil.rmtree(rl_paths.untracked_folder())

__location__ = get_main_dir()
def main():
    if not os.path.isfile(__location__+"\\rocketleague.db"):
        import db_setup
        db_setup.initdb()

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
    root.protocol("WM_DELETE_WINDOW",lambda : on_exit(rman,root))
    root.mainloop()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "restore":
        restore()


