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

    def add_replay(self, filename, name, mapname):
        with self.conn:
            self.conn.execute("INSERT INTO replays VALUES (?, ?, ?);", filename, name, mapname)
            dprint("Inserted %s %s %s into replays ", filename,name,mapname)

    def add_team(self,ID,teamNum,player_name,goals=None,saves=None):
        with self.conn:
            self.conn.execute("INSERT INTO teams VALUES (? ? ? ? ?);",ID,teamNum,player_name,goals,saves)
        
    def add_tag(self):
        pass
        
    def add_match_data(self):
        pass

    def add_note(self):
        pass

    def add_group(self):
        pass

    def close(self):   
        self.conn.close()


    def __enter__(self):
        pass

    def __exit(self):
        self.close()


    def dprint(self,msg,*arg):
        if self.debug:
            print msg % arg