#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information
from Tkinter import *
import tkFileDialog
import ttk
import gui.HandlerApplication as cst
import threading
import sys
import os
import rl_paths
import shutil
import imp
import impexp.RLExport as RLExport
import impexp.RLImport as RLImport
import logging
import traceback
import gui.Popups as Popups
from os.path import expanduser
import os.path
import tkMessageBox
logger = logging.getLogger("root")


def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])

def export_single_func(app):
    if app.tracked_replays.has_selected_item():
        data = RLExport.convert2json(app.tracked_replays.get_selected_item())
        RLExport.dump_to_zip([data])
        tkMessageBox.showinfo(title="Export",message="Export complete!")

def export_many_func(app):
    if app.tracked_replays.size() > 0:
        d = Popups.ExportPopup(winfo_rootc=(app.winfo_rootx(),app.winfo_rooty()),listitems=app.tracked_replays.variables)
        app.wait_window(d)
        if hasattr(d,"selection"):
            data = RLExport.convertreplays2json(d.selection)
            RLExport.dump_to_zip(data)
            tkMessageBox.showinfo(title="Export",message="Export complete!")

def import_func(app):
    filename = tkFileDialog.askopenfilename(initialdir=os.path.join(expanduser("~"),"Downloads"),defaultextension=".zip")
    print filename
    if filename:
        RLImport.import_zip(filename)

def read_replay_path():
    with open("replay.path","r") as f:
        for line in f:
            rl_paths._default_path = line.strip()
            break

def determine_replaydir():
    if os.path.isfile("replay.path"):
        print "have path"
        read_replay_path()
        return

    if not os.path.isdir(rl_paths.demo_folder()):
        print "Demo folder not in default location"
        if not os.path.isfile("replay.path"):
            print "Replay folder not in default location"
            tkMessageBox.showinfo(title="Replay Directory",message="Your replay directory is not in the default selection.\nPlease select its location from the next dialog.")
            dirpath = tkFileDialog.askdirectory(title="Select Replay Directory",initialdir=os.path.expanduser("~"))
            rl_paths._default_path = dirpath
            with open("replay.path",'w') as f:
                f.write(dirpath)
                f.write("\n")
        else:
            read_replay_path()
        print "DEFAULT: ",rl_paths._default_path
        print "DEMO: ",rl_paths.demo_folder()

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
        root = Tk()
        determine_replaydir()
        if not os.path.isfile(os.path.join(__location__,"rocketleague.db")):
            import db_setup
            db_setup.initdb()
        #If untracked folder move everything to demo folder for new processing method.
        if os.path.isdir(rl_paths.untracked_folder()):
            for f in os.listdir(rl_paths.untracked_folder()):
                f = os.path.splitext(f)[0]
                shutil.move(rl_paths.untracked_folder(f),rl_paths.demo_folder(f))

        
        root.title("Rocket League Replay Handler")
        root.minsize(700,500)
      

        rman = cst.ReplayManager(root)
        rman.pack(expand=True,fill=BOTH)

        menu = Menu(root)
        root.config(menu=menu)

        filemenu = Menu(menu,tearoff=0)
        #menu.add_cascade(label="File", menu=filemenu)
        menu.add_command(label="Import", command=lambda : import_func(rman))
        menu.add_command(label="Export Selected", command=lambda : export_single_func(rman))
        menu.add_command(label="Export Multiple", command=lambda : export_many_func(rman))
        menu.add_command(label="Edit Selected",command=rman.edit)
        menu.add_command(label="Rescan",command=rman.process_new)
        root.protocol("WM_DELETE_WINDOW",lambda : on_exit(rman,root))
        root.mainloop()
    except Exception, e:
        logger.error("Encountered uncaught error")
        logger.error("Error was: %s", e)
        logger.error("%s",sys.exc_info())
        print "Error",e,sys.exc_info()
        print traceback.format_exc()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2 and (sys.argv[1].lower() == "restore" or sys.argv[1].lower() == "reset"):
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
            logger.error("%s",sys.exc_info())
            print "Error",e,sys.exc_info()
            print traceback.format_exc()


