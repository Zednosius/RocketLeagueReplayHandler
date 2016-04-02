#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import zipfile
import json
import rl_paths
import logging
import time
from db_manager import *
logger = logging.getLogger(__name__)

def convertreplays2json(replay_list):
    """
    Converts several replays data into json.
    """
    converts = []
    for replay in replay_list:
        converts.append(convert2json(replay))
    return converts

def convert2json(replay_vars):
    """
    Converts a replays data into json.
    """
    data = {}
    #Replay associated
    data['filename'] = replay_vars[1]
    data['name'] = replay_vars[2]
    data['map'] = replay_vars[3]
    data['date'] = replay_vars[4]
    #Data from DB
    fill_with_db_items(replay_vars[0],data)
    logger.debug("DATA: ",data)
    return data

def fill_with_db_items(ID, data):
    """
    Fetches DB data related to the replay having ID as id.
    """
    with DB_Manager() as dmann:
        data['teams']  = [x[1:] for x in dmann.get_all_where("teams",id=("=",ID))]
        data['tags']   = [x[1:] for x in dmann.get_all_where("tags",id=("=",ID)) ]
        data['notes']  = [x[1:] for x in dmann.get_all_where("notes",id=("=",ID))]
        data['groups'] = dmann.get_groups(ID)

def dump_to_zip(jsondata):
    """
    Dumps jsondata alongside the actual replay files the jsondata describes into a zipfile.
    """
    with zipfile.ZipFile("RL_"+time.strftime("%Y-%m-%d_%H-%M-%S")+".zip","w") as fzip:
        fzip.writestr("data.json",json.dumps(jsondata,separators=(",",":"),sort_keys=True,indent=1))
        if type(jsondata) == list:
            for replay in jsondata:
                fzip.write(rl_paths.tracked_folder(replay['filename']),replay['filename']+".replay")
        else:
            raise ValueError("jsondata must be list of dicts")

    print "Created zipfile"

