#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import sqlite3
import sys
import os


def clean(string):
    return ''.join(c for c in string if c.isalnum())

def combine_dicts(*args):

    d = {}
    for dic in args:
        for k in dic:
            d[k] = dic[k]
    return d

class DB_Manager():
    """
    Abstracts away the more low level database interactions.
    
    Use either 'with DB_Manager() as foo' or create it and the call close() when done.
    """
    def __init__(self,debug=False):
        self.conn = sqlite3.connect("rocketleague.db")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.debug = debug

    def add_replay(self, filename, name, mapname, datetime):
        with self.conn:
            self.conn.execute("INSERT INTO replays (filename,name,map,datetime) VALUES (?, ?, ?, ?);", (filename, name, mapname,datetime))
            self.dprint("Inserted %s %s %s %s into replays ",filename,name,mapname,datetime)

    def add_team(self,ID,teamNum,player_name,goals=None,saves=None):
        with self.conn:
            self.conn.execute("INSERT INTO teams VALUES (?, ?, ?, ?, ?);",(ID,teamNum,player_name,goals,saves))
            self.dprint("Inserted %s %s %s %s %s into teams",ID,teamNum,player_name,goals,saves)

    def add_tag(self,ID,tagname,timestamp):
        with self.conn:
            self.conn.execute("INSERT INTO tags VALUES (?, ?, ?);",(ID,tagname,timestamp))
            self.dprint("Inserted %s %s %s into tags",ID,tagname,timestamp)

    def add_match_data(self,ID,teamNum,goals,saves):
        with self.conn:
            self.conn.execute("INSERT INTO match_data VALUES (?, ?, ?, ?);",(ID,teamNum,goals,saves))
            self.dprint("Inserted %s %s %s %s into match_data", ID,teamNum,goals,saves)

    def add_note(self, ID, note):
        with self.conn:
            self.conn.execute("INSERT INTO notes VALUES (?, ?);",(ID,note))
            self.dprint("Inserted %s %s into notes",ID,note)

    def update_note(self,ID,note):
        with self.conn:
            self.conn.execute("UPDATE notes SET note=? WHERE id=?",(note,ID))
            self.dprint("Updated note %s",ID)

    def add_group(self, group_name):
        with self.conn:
            self.conn.execute("INSERT INTO groups (name) VALUES (?);", (group_name,))
            self.dprint("Inserted %s into groups",group_name)

    def add_replay_to_group(self, ID, gID):
        with self.conn:
            self.conn.execute("INSERT INTO group_members VALUES (?, ?);")
            self.dprint("Inserted %s %s into group_members",ID,gID)

    def get_all(self, table):
        """Get all the rows from specified table"""
        table = clean(table)
        with self.conn:
            return self.conn.execute("SELECT * FROM "+table).fetchall()

    def get_all_where(self,table,**kw):
        """Get all the rows from specified table where all conditions are satisfied
            conditions are passed as cond1=(cmp,var1),cond2=(cmp,var2)
        """
        table = clean(table)
        for k in kw.keys():
            if(type(kw[k]) == str):
                kw[k] = clean(kw[k])

        where_clause = " AND ".join([" %s %s :%s" % (key,kw[key][0],key) for key in kw.keys()])
        kw = {k:v[1] for (k,v) in kw.items()}
        self.dprint("SELECT * FROM "+table+" WHERE "+where_clause)
        print "allw kws: ",kw
        with self.conn:
            return self.conn.execute("SELECT * FROM "+table+" WHERE "+where_clause,kw).fetchall()

    def filter_replays(self,replayfilters={},tagfilters={},playerfilters={},groupfilters={}):
        print replayfilters,tagfilters,playerfilters,groupfilters
        query = "SELECT * FROM replays R " 
        if replayfilters:
            replay_where = self.get_where_clause("R",replayfilters)
            query += "where " + replay_where

        if tagfilters:
            tag_where = self.get_where_clause("T",tagfilters)
            tag_select = "SELECT * FROM tags T where R.id = T.id AND " + tag_where
            query += " AND EXISTS("+tag_select+")"

        if playerfilters:
            player_where = self.get_where_clause("P",playerfilters)
            player_select ="SELECT * from teams P where R.id = P.id AND "+player_where
            query += " AND EXISTS("+player_select+")"

        if groupfilters:
            group_where = self.get_where_clause("GM",groupfilters)
            group_select = "SELECT * FROM group G inner join group_members GM on G.g_id=GM.g_id WHERE R.id=G.id "+group_where
            query += " AND EXISTS("+group_select+")"

        kw = combine_dicts(replayfilters,tagfilters,playerfilters,groupfilters)
        print "keys: ",kw
        kw = {k:v[1] for (k,v) in kw.items()}
        print "query:",query,"kws:",kw

        with self.conn:
            return self.conn.execute(query,kw).fetchall()

        "SELECT * FROM replays R WHERE <replayfilters>  \
        AND EXISTS (SELECT T.id FROM tags T WHERE <tagfilters>) \
        AND EXISTS (SELECT P.id FROM teams P WHERE <playerfilters>\
        AND EXISTS (SELECT G.id FROM (SELECT * from group g inner join group_members gm on g.g_id=gm.g_id AND g.name=groupname"
    def close(self):   
        self.conn.close()


    def __enter__(self):
        return self

    def __exit__(self ,type, value, traceback):
        self.close()

    def get_where_clause(self,table_alias,kw):
        return " AND ".join([table_alias+".%s %s :%s" % (key,kw[key][0],key) for key in kw.keys()])

    def dprint(self,msg,*arg):
        if self.debug:
            print msg % arg

if __name__ == '__main__':
    with DB_Manager(debug=True) as mann:
        # print mann.get_all("replays")
        # print mann.get_all_where("replays",filename=("=","hurr"))
        # print mann.get_all_where("replays",map=("=","Durrtown"))
        # print mann.get_all_where("replays",id=(">",1))
        mann.get_all_where("replays",id=(">",1),map=("=","DFH Stadium"))
        print mann.filter_replays(replayfilters=dict(map=("=","DFH Stadium")),tagfilters=dict(),playerfilters=dict(playername=("=","C-Block")),groupfilters=dict())