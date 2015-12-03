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
    t = threading.Thread(target=thread_func,args=[func,args],kwargs={"queue":resultqueue})
    t.start()
    widget.after(25, result_checking,widget,add_func,resultqueue)
    return (t,resultqueue)

def thread_func(func,args,**kwargs):
    try:
        print args
        func(*args,**kwargs)
    except Exception, e:
        print "Something went wrong in a thread function"
        print "Error",e
        logger.error("Error in thread function %s",func)
        logger.error("Error was %s",e)
        kwargs['queue'].stopnow = True
        raise

def result_checking(widget, add_func, resultqueue):
    """
    Listens for results on resultqueue, For a certain widget.
    When a result has arrived it is sent to add_func
    then it checks again after 50ms.
    """
    try:
        v = resultqueue.get(block=False)
        if v == QueueOp.STOP or hasattr(resultqueue,"stopnow"):
            return
        if add_func:
            add_func(v)
    except Queue.Empty, e:
        pass
    widget.after(25,result_checking,widget,add_func,resultqueue)

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

def edit_update(original,updated,queue):
    org_teams = original['teams']
    new_teams = updated['teams']
    org_headers = original['headers']
    new_headers =  updated['headers']
    print "Updating Entry"
    with DB_Manager() as dmann:
        print "headers",org_headers,new_headers
        if  org_headers != new_headers:
            dmann.update_replay(org_headers,new_headers)
            logger.debug("Updated replay header from %s to %s",org_headers,new_headers)
            print "Updated replay header from %s to %s " % (org_headers,new_headers)

        for i in range(0,len(new_teams)):
            if i < len(org_teams):
                if org_teams[i] != new_teams[i]:
                    dmann.update_team(org_teams[i],new_teams[i])
                    logger.debug("Updated team entry %s to %s",org_teams[i],new_teams[i])
                    #print "Changed from %s to %s" % (org_teams[i],new_teams[i])
            else:
                #print "added %s" % (new_teams[i],)
                dmann.add_team(*new_teams[i])
                logger.debug("Added team entry %s",new_teams[i])
    print "Update finished"
    queue.put(updated)
    queue.put(QueueOp.STOP)


def fetch_replays(replayfilters={},tagfilters={},playerfilters={},groupfilters={},queue=None):
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
        queue.put(
            (replay, os.path.isfile(rl_paths.demo_folder(replay[1])))
            )

    logger.info("Inserted replays into tracked_replay_list")
    print "Fetch replays done"
    queue.put(QueueOp.STOP)

def fetch_display_data(replay,queue):
    display_data = {}
    with DB_Manager() as mann:
        display_data['headers'] = list(replay)
        display_data['teams']  = mann.get_all_where("teams",id=("=",replay[0]))
        display_data['tags']    = mann.get_all_where("tags",id=("=",replay[0]))
        display_data['notes']   = mann.get_all_where("notes",id=("=",replay[0]))
        display_data['groups']  = mann.get_groups(replay[0])
    queue.put(display_data)
    queue.put(QueueOp.STOP)


def save_data(data,queue):
    with DB_Manager() as dmann:
        id_ = data['id']
        txt = data['note']
        logger.debug("Updating %ss note: %s " ,id_,txt)
        dmann.update_note(id_, txt)
    queue.put(QueueOp.STOP)

def startup_procedure(queue):
    print "Running startup procedure"
    dlist = []
    _scan_demo_folder(dlist)
    print "Scan complete"
    _process_new_replays(dlist)
    print "Process complete"
    fetch_replays(queue=queue)
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
    #print "_Processing new replays",dlist
    parser =  replay_parser.ReplayParser()
    tdict = {}
    new_list = []

    for d in dlist:
        if not d['tracked']:
            #print "Processing",d
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
    #print replay
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

def remove_group(ID,groupname,queue):
    with DB_Manager() as dmann:
        dmann.delete_from_group(ID,groupname)
    queue.put(QueueOp.STOP)

def remove_tag(ID,tagname,tagtime,queue):
    with DB_Manager() as dmann:
        dmann.delete_tag(ID,tagname,tagtime)
    queue.put(QueueOp.STOP)

def insert_scanned_staged(self):
    logger.info("Inserting scanned staged files into staged list")
    count = 0
    with DB_Manager() as dmann:
        for entry in self.demo_scan:
            if entry['tracked']:
                count += 1
                var = dmann.get_all_where("replays",filename=("=",entry["name"]))[0]
                if self.staged_list.size() == 0: 
                    self.staged_list.insert("end",var[2],var)
                else:
                    for i,v in enumerate(self.staged_list.variables):
                        #Insert based on date
                        if v[4] < var[4]:
                            self.staged_list.insert(i,var[2],var)
                            break
                        elif i+1 == self.staged_list.size():
                            self.staged_list.insert("end",var[2],var)
                            break
                logger.debug("Inserted staged replay %s",entry['name'])
    logger.info("Inserted total of %s staged replays",count)
    logger.info("Staged files insertion complete")