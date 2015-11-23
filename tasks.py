#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import threading
import Queue
from db_manager import DB_Manager
import os
import os.path
import shutil
import logging
import time
import rl_paths
logger = logging.getLogger(__name__)

class QueueOp:
    STOP =0

def start_task(widget, add_func, func, *args):
    resultqueue = Queue.Queue()
    """
    Starts a task with the target function and arguments, results are sent to the add_func which should be a classmethod of the widget.
    """
    threading.Thread(target=func,args=args,kwargs={"queue":resultqueue}).start()
    widget.after(50, result_checking,widget,add_func,resultqueue)

def result_checking(widget, add_func, resultqueue):
    """
    Listens for results on resultqueue, For a certain widget.
    When a result has arrived it is sent to add_func
    then it checks again after 50ms.
    """
    try:
        v = resultqueue.get(block=False)
        print "Found on queue",v
        if v == QueueOp.STOP:
            return

        add_func(v)
    except Exception, e:
        print "Excepted",e
        pass
    widget.after(50,result_checking,widget,add_func,resultqueue)

def copy_to_staging(variables, queue):
    if not os.path.isfile(rl_paths.demo_folder(variables[1])):
        shutil.copy2(rl_paths.tracked_folder(variables[1]),rl_paths.demo_folder(variables[1]))
        logger.info("Copied %s to demo_folder",variables[1])

    if not os.path.isfile(rl_paths.tracked_folder(variables[1])):
        shutil.copy2(rl_paths.demo_folder(variables[1]),rl_paths.tracked_folder(variables[1]))
        logger.info("Copied %s to tracked folder",variables[1])

    if not os.path.isfile(rl_paths.backup_folder(variables[1])):
        shutil.copy2(rl_paths.demo_folder(variables[1]),rl_paths.backup_folder(variables[1]))
        logger.info("Copied %s to backup folder",variables[1])
    queue.put(QueueOp.STOP)


def fetch_replays(queue,replayfilters={},tagfilters={},playerfilters={},groupfilters={}):
    logger.info("Fetching replays")
    with DB_Manager() as mann:
        if replayfilters  or tagfilters or playerfilters or groupfilters:
            replays = mann.filter_replays(replayfilters,tagfilters,playerfilters,groupfilters)
            logger.debug("Fetched replays from database with parameters %s %s %s %s",
                replayfilters,tagfilters,playerfilters,groupfilters)
        else:
            replays = mann.get_all("replays","date_time desc")
            logger.debug("Fetched all replays (paramless)")

    print "REPLAYS: ",replays

    for replay in replays:
        if not os.path.isfile(rl_paths.tracked_folder(replay[1])) and os.path.isfile(rl_paths.backup_folder(replay[1])):
            shutil.copy2(rl_paths.backup_folder(replay[1]), rl_paths.tracked_folder(replay[1]))
            logger.info("Restored missing replay %s from backup",replay[1])
        print "Putting replay",replay
        queue.put(replay)

    logger.info("Inserted replays into tracked_replay_list")
    queue.put(QueueOp.STOP)

def scan_demo_folder(queue):
    logger.info("Scanning demo on path %s",rl_paths.demo_folder())
    with DB_Manager(debug=True) as dmann:
        l = [rl_paths.demo_folder( os.path.splitext(x)[0]) 
            for x in os.listdir(rl_paths.demo_folder()) 
            if os.path.isfile(rl_paths.demo_folder(os.path.splitext(x)[0]))]
        l.sort(reverse=True,key=lambda x: os.path.getmtime(x))
        logger.info("Sorted replays by date")
        for f in l:
            filename = os.path.splitext(os.path.basename(f))[0]
            res = ""
            if os.path.isfile(f) and not dmann.replay_exists(filename):
                res = {"path":f,"name":filename,"tracked":False}
                queue.put(res)
            elif os.path.isfile(f):
                res = {"path":f,"name":filename,"tracked":True}
                queue.put(res)
            else:
                continue
            logger.debug("Scanning %s resulted in %s",filename,res)
    logger.info("Appended all %s replays",len(l))
    queue.put(QueueOp.STOP)

