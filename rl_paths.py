#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import shutil
import os
from os.path import expanduser
import errno
_default_path = "\Documents\My Games\Rocket League\TAGame\Demos"



def make_dirs():
    try:
        os.makedirs(expanduser("~")+_default_path+"\\tracked")

    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    try:
        os.makedirs(expanduser("~")+_default_path+"\\untracked") 
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    try:
        os.makedirs(expanduser("~")+_default_path+"\\backup")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
            
def demo_folder():
    demofolder = expanduser("~")+_default_path
    return demofolder

def untracked_folder(f=None):
    return demo_folder() + "\\untracked" + ("\\"+f+".replay" if f else "")

def tracked_folder(f = None):
    return demo_folder() + "\\tracked" + ("\\"+f+".replay" if f else "")

def backup_folder(f=None):
    return demo_folder() + "\\backup" + ("\\"+f+".replay" if f else "")