#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information


import sqlite3
import sys


def initdb():

  # print the connection string we will use to connect
    print "Connecting to database"
    conn = sqlite3.connect("rocketleague.db")
    conn.execute("PRAGMA foreign_keys = ON")
    with conn:      

        #ID; FILENAME; NAME; MAP;
        conn.execute("CREATE TABLE replays (id INTEGER PRIMARY KEY,filename varchar(64),name text,map text,datetime text);")
        
        #ID(fk); TEAM; PLAYERCOUNT; GOALS;  (information about a team in a match)
        conn.execute("CREATE TABLE match_data (id integer REFERENCES replays ON DELETE CASCADE, team integer, playercount integer, goals integer, saves integer);")
        
        #ID(fk);TEAM; PLAYERNAME; GOALS; SAVES; (information about a player in a match)
        conn.execute("CREATE TABLE teams (id integer REFERENCES replays ON DELETE CASCADE, team integer, playername text, goals integer, saves integer);")
        
        #ID(fk);TAGNAME;TIMESTAMP; (User created time tags for a match)
        conn.execute("CREATE TABLE tags (id integer REFERENCES replays ON DELETE CASCADE, tagname text, timestamp integer);")
        
        #ID(fk); NOTE; (Other notes that doesn't have a timestamp)
        conn.execute("CREATE TABLE notes (id integer REFERENCES replays ON DELETE CASCADE, note text);")
        
        #ID;NAME; (For grouping a set of replays together) 
        conn.execute("CREATE TABLE groups (g_id integer PRIMARY KEY, name text);")

        #Many-to-Many relation
        conn.execute("CREATE TABLE group_members (g_id integer REFERENCES groups ON DELETE CASCADE, id integer REFERENCES replays ON DELETE CASCADE);")

        print "Success!"
    conn.close()
if __name__ == "__main__":
    if len(sys.argv) == 1:
        initdb()
