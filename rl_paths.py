#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import shutil
import os
from os.path import expanduser
import errno
_default_path = "Documents\\My Games\\Rocket League\\TAGame\\Demos"



def make_dirs():
    try:
        os.makedirs(os.path.join(expanduser("~"),_default_path,"tracked"))

    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    try:
        os.makedirs(os.path.join(expanduser("~"),_default_path,"untracked"))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    try:
        os.makedirs(os.path.join(expanduser("~"),_default_path,"backup"))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
            
def _add_ext_or_empty(f):
    return (f+".replay" if f else "")

def demo_folder(f=None):
    demofolder = os.path.join(expanduser("~"),_default_path,_add_ext_or_empty(f))
    return demofolder

def untracked_folder(f=None):
    return os.path.join(demo_folder(),"untracked",_add_ext_or_empty(f))

def tracked_folder(f = None):
    return os.path.join(demo_folder(),"tracked", _add_ext_or_empty(f))

def backup_folder(f=None):
    return os.path.join(demo_folder(),"backup", _add_ext_or_empty(f))