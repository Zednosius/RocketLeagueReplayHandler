#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import sqlite3
import sys
import os
import TABLES



class DB_Manager():
    """
    Abstracts away the more low level database interactions.
    
    Use either 'with DB_Manager() as foo' or create it and the call close() when done.
    """
    def __init__(self,debug=False):
        self.conn = sqlite3.connect("rocketleague.db")
        self.conn.execute("PRAGMA foreign_keys = ON")

    def add_replay(self, filename, name, mapname, datetime):
        with self.conn:
            self.conn.execute("INSERT INTO replays (filename,name,map,datetime) VALUES (?, ?, ?, ?);", filename, name, mapname,datetime)
            self.dprint("Inserted %s %s %s into replays ", filename,name,mapname,datetime)

    def add_team(self,ID,teamNum,player_name,goals=None,saves=None):
        with self.conn:
            self.conn.execute("INSERT INTO teams VALUES (?, ?, ?, ?, ?);",ID,teamNum,player_name,goals,saves)
            self.dprint("Inserted %s %s %s %s %s into teams",ID,teamNum,player_name,goals,saves)

    def add_tag(self,ID,tagname,timestamp):
        with self.conn:
            self.conn.execute("INSERT INTO tags VALUES (?, ?, ?);",ID,tagname,timestamp)
            self.dprint("Inserted %s %s %s into tags",ID,tagname,timestamp)

    def add_match_data(self,ID,teamNum,goals,saves):
        with self.conn:
            self.conn.execute("INSERT INTO match_data VALUES (?, ?, ?, ?);",ID,teamNum,goals,saves)
            self.dprint("Inserted %s %s %s %s into match_data", ID,teamNum,goals,saves)

    def add_note(self, ID, note):
        with self.conn:
            self.conn.execute("INSERT INTO notes VALUES (?, ?);",ID,note)
            self.dprint("Inserted %s %s into notes",ID,note)

    def add_group(self, group_name):
        with self.conn:
            self.conn.execute("INSERT INTO groups (name) VALUES (?);", group_name)
            self.dprint("Inserted %s into groups",group_name)

    def add_replay_to_group(self, ID, gID):
        with self.conn:
            self.conn.execute("INSERT INTO group_members VALUES (?, ?);")
            self.dprint("Inserted %s %s into group_members",ID,gID)

    def close(self):   
        self.conn.close()


    def __enter__(self):
        pass

    def __exit(self):
        self.close()


    def dprint(self,msg,*arg):
        if self.debug:
            print msg % arg