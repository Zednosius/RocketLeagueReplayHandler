#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
from Tkinter import *
import ttk
import gui.HandlerApplication as cst
import threading
import sys
import os
import rl_paths
import shutil
import imp
import impexp.RLExport as RLExport
import logging
logger = logging.getLogger("root")


def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])
def export_func(app):
    if app.tracked_replays.has_selected_item():
        data = RLExport.convert2json(app.tracked_replays.get_selected_item())
        print "data: ",data
        print "Creating zip"
        RLExport.dump_to_zip(data)


def output():
    print "Not implemented"

def on_exit(rman,root):
    rman.save()
    root.destroy()

def restore(var):

    print "Restoring demo folder"
    logger.info("Restoring demo folder to its original state")
    logger.info("Path to backups: %s",rl_paths.backup_folder())
    logger.debug("Files there: %s",os.listdir(rl_paths.backup_folder()))
    for f in os.listdir(rl_paths.backup_folder()):
        f = os.path.splitext(f)[0]
        src = rl_paths.backup_folder(f)
        dst = rl_paths.demo_folder(f)
        shutil.copy2(src,dst)
        logger.debug("Copied from %s to %s",src,dst)

    shutil.rmtree(rl_paths.tracked_folder())
    shutil.rmtree(rl_paths.untracked_folder())
    logger.info("Removed tracked and untracked folder")
    logger.info("Restore Complete!")
    var.set("Demo folder restored!")

__location__ = get_main_dir()
def main():
    print "Starting application"
    try:
        if not os.path.isfile(__location__+"\\rocketleague.db"):
            import db_setup
            db_setup.initdb()

        root = Tk()
        root.title("Rocket League Replay Handler")
        root.minsize(700,500)
      

        rman = cst.ReplayManager(root)
        rman.pack(expand=True,fill=BOTH)

        menu = Menu(root)
        root.config(menu=menu)

        filemenu = Menu(menu,tearoff=0)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Import", command=output)
        filemenu.add_command(label="Export", command=lambda : export_func(rman))


        root.protocol("WM_DELETE_WINDOW",lambda : on_exit(rman,root))
        root.mainloop()
    except Exception, e:
        logger.error("Encountered uncaught error")
        logger.error("Error was: %s", e)
        print e

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "restore":
        try:
            root = Tk()
            root.title("Rocket League Replay Handler")
            var = StringVar()
            var.set("Restoring replay folder to original state")
            threading.Thread(target=restore,args=[var]).start()
            Label(root,textvariable=var).pack()
            root.mainloop()
        except Exception, e:
            logger.error("Encountered uncaught error")
            logger.error("Error was: %s", e)
            print e


