#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import threading
import Queue
import sqlite3
from db_manager import DB_Manager
import os
import os.path
import shutil
import logging
import time
import rl_paths
import replay_parser
import datetime
import names
import re
logger = logging.getLogger(__name__)

class QueueOp:
    STOP =0

def start_task(widget, add_func, func, *args):
    resultqueue = Queue.Queue()
    """
    Starts a task with the target function and arguments, results are sent to the add_func which should be a classmethod of the widget.
    """
    t = threading.Thread(target=func,args=args,kwargs={"queue":resultqueue})
    t.start()
    widget.after(50, result_checking,widget,add_func,resultqueue)
    return t

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
        if add_func:
            add_func(v)
    except Queue.Empty, e:
        print "Excepted",e
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

    # print "REPLAYS: ",replays

    for replay in replays:
        if not os.path.isfile(rl_paths.tracked_folder(replay[1])) and os.path.isfile(rl_paths.backup_folder(replay[1])):
            shutil.copy2(rl_paths.backup_folder(replay[1]), rl_paths.tracked_folder(replay[1]))
            logger.info("Restored missing replay %s from backup",replay[1])
        # print "Putting replay",replay
        queue.put(replay)

    logger.info("Inserted replays into tracked_replay_list")
    queue.put(QueueOp.STOP)

def startup_procedure(queue):
    print "Running startup procedure"
    dlist = []
    _scan_demo_folder(dlist)
    print "Scan complete"
    _process_new_replays(dlist)
    print "Process complete"
    fetch_replays(queue)
    print "Fetched"
    queue.put(QueueOp.STOP)

def scan_refresh(queue):
    dlist = []
    _scan_demo_folder(dlist)
    _process_new_replays(dlist)
    queue.put(QueueOp.STOP)

def _scan_demo_folder(dlist):
    # print "scanning on",rl_paths.demo_folder()
    logger.info("Scanning demo on path %s",rl_paths.demo_folder())
    with DB_Manager(debug=True) as dmann:
        l = [rl_paths.demo_folder( os.path.splitext(x)[0]) 
            for x in os.listdir(rl_paths.demo_folder()) 
            if os.path.isfile(rl_paths.demo_folder(os.path.splitext(x)[0]))]
        l.sort(reverse=True,key=lambda x: os.path.getmtime(x))
        # print "Sorted replays by date"
        logger.info("Sorted replays by date")
        for f in l:
            filename = os.path.splitext(os.path.basename(f))[0]
            res = ""
            if os.path.isfile(f) and not dmann.replay_exists(filename):
                res = {"path":f,"name":filename,"tracked":False}
                dlist.append(res)
            elif os.path.isfile(f):
                res = {"path":f,"name":filename,"tracked":True}
                dlist.append(res)
            else:
                continue
            logger.debug("Scanning %s resulted in %s",filename,res)
            # print "Scanning %s resulted in %s"%(filename,res)
    logger.info("Appended all %s replays",len(l))

def _process_new_replays(dlist):
    print "_Processing new replays",dlist
    parser =  replay_parser.ReplayParser()
    tdict = {}
    new_list = []

    for d in dlist:
        if not d['tracked']:
            print "Processing",d
            data = parser.parse(d['path'])
            path = d['path']
            #Correct the file modified time if it is discrepant with the internal date from the replay file.
            #A discrepancy most probably means the replay was downloaded from somewhere.
            #Correcting the time makes it easier to find it in the replay browser ingame, because it will line up with its staged counterpart
            repTime = time.mktime(datetime.datetime(*map(int,data['header']['Date'].replace(":","-").split("-"))).timetuple())

            ftime = os.path.getmtime(path)
            if repTime != ftime:
                os.utime(path,(repTime,repTime))
                logger.info("Changed time of %s to %s from %s",path,repTime,ftime)

            time_ = re.sub(":(\d\d)-"," \\1:",data['header']['Date'])
            replay = _parse_to_useful(d,data)
            _insert_new_replay_into_database(replay)
            #Insert into database


def _parse_to_useful(replay_base,data):
    replay = {}
    replay['filename'] = replay_base['name']
    replay['date'] = re.sub(":(\d\d)-"," \\1:",data['header']['Date'])
    replay['name'] = "Replay "+replay['date']
    replay['mapname'] = names.stadiums.get(data['header']['MapName'].lower(),data['header']['MapName'])
    
    teams = []
    logger.debug("Displaying new variables: %s",replay_base)

    #New replay
    if 'PlayerStats' in data['header'].keys():
        logger.info("Replay was in new format")
        for ps in data['header']['PlayerStats']:
            teams.append(
                (None,ps.get('Name', None).decode('unicode-escape'),
                    ps.get('Team', None),
                    ps.get('Goals', None),
                    ps.get('Saves', None),
                    ps.get('Shots', None),
                    ps.get('Assists', None),
                    ps.get('Score', None))
                )
        logger.debug("Parsed data was : %s",teams)

    else:

        logger.info("Replay was in old format")
        #Old replay
        names_goals = {}
        for d in data['header']['Goals']:
            if "PlayerName" in d:
                names_goals[d['PlayerName'].decode('unicode-escape')] = (1 + names_goals.get("PlayerName",[0])[0],d['PlayerTeam'])
        
        for k,v in names_goals.items():
            teams.append((None,k,int(names_goals[k][1]),names_goals[k][0])+("",)*4)
        logger.debug("Parsed data was : %s",teams)

    replay['teams'] = teams
    print replay
    return replay

def _insert_new_replay_into_database(replay):
    try:
        with DB_Manager(debug=True) as dmann:
            #Create a replay entry and get the id.

            c = dmann.add_replay(filename=replay['filename'],name=replay['name'], mapname=replay['mapname'], date_time=replay['date'])
            idx = c.lastrowid
            logger.debug("Created replay: %s",replay)

            #Make list of tuples to be inserted into database
            teams = [(idx,)+player[1:] for player in replay['teams']]
            logger.debug("Inserting teams: %s",teams)
            dmann.add_many_team(teams)
            dmann.add_note(idx,"")
            logger.info("Replay added")
            shutil.copy2(rl_paths.demo_folder(replay['filename']),rl_paths.backup_folder(replay['filename']))
            shutil.move(rl_paths.demo_folder(replay['filename']),rl_paths.backup_folder(replay['filename']))

    except sqlite3.IntegrityError, e:
        self.notif_text.set("ERROR: COULD NOT CREATE ENTRY\n"+str(e))
        logger.error("Could not create entry")
        logger.error("Error : %s",e)
        raise


