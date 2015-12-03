#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import sqlite3
import sys
import os
import logging
logger = logging.getLogger(__name__)

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
    def __init__(self,loc="rocketleague.db",debug=False):
        self.conn = sqlite3.connect(loc)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.debug = debug

    def add_replay(self, filename, name, mapname, date_time):
        logger.info("Inserted %s %s %s %s into replays ",filename,name,mapname,date_time)
        return self.conn.execute("INSERT INTO replays (filename,name,map,date_time) VALUES (?, ?, ?, ?);", (filename, name, mapname,date_time))

    def update_replay(self, original, replacement):
        logger.info("Updating replay with filename=%s,name=%s,map=%s,date_time=%s WHERE id=%s",replacement[1:]+original[0:1])
        return self.conn.execute("UPDATE replays SET filename=?,name=?,map=?,date_time=? WHERE id=?",replacement[1:]+original[0:1])

    def replay_exists(self,filename):
        return self.conn.execute("SELECT 1 from replays WHERE filename=?",(filename,)).fetchone()

    def add_team(self,ID,player_name,teamNum,goals=None,saves=None,shots=None,assists=None,score=None):
        logger.info("Inserted %s %s %s %s %s %s %s %s into teams",ID,player_name,teamNum,goals,saves,shots,assists,score)
        return self.conn.execute("INSERT INTO teams VALUES (?, ?, ?, ?, ?, ?, ?, ?);",(ID,player_name,teamNum,goals,saves,shots,assists,score))

    def add_many_team(self,list_of_tuples):
        return self.conn.executemany("INSERT INTO teams VALUES (?, ?, ?, ?, ?, ?, ?, ?);",list_of_tuples)

    def update_team(self, original, replacement):
        print "Update team %s : %s" % (original, replacement)
        data = replacement+original[:2]
        logger.info("Ran UPDATE teams SET id=%s,playername=%s,,team=%s,goals=%s,saves=%s,shots=%s,assists=%s,score=%s WHERE id=%s AND playername=%s", data)
        return self.conn.execute("UPDATE teams SET id=?,playername=?,team=?,goals=?,saves=?,shots=?,assists=?,score=? WHERE id=? AND playername=?;", data)

    def add_tag(self,ID,tagname,timestamp):
        logger.info("Inserted %s %s %s into tags",ID,tagname,timestamp)
        return self.conn.execute("INSERT INTO tags VALUES (?, ?, ?);",(ID,tagname,timestamp))

    def add_match_data(self,ID,teamNum,goals,saves):
        logger.info("Inserted %s %s %s %s into match_data", ID,teamNum,goals,saves)
        return self.conn.execute("INSERT INTO match_data VALUES (?, ?, ?, ?);",(ID,teamNum,goals,saves))

    def add_note(self, ID, note):
        logger.info("Inserted %s %s into notes",ID,note)
        return self.conn.execute("INSERT INTO notes VALUES (?, ?);",(ID,note))

    def update_note(self,ID,note):
        logger.info("Updated note %s with text '%s'",ID,note)
        return self.conn.execute("UPDATE notes SET note=? WHERE id=?",(note,ID))

    def add_group(self, group_name):
        logger.info("Inserted %s into groups",group_name)
        return self.conn.execute("INSERT INTO groups (name) VALUES (?);", (group_name,))

    def add_replay_to_group(self, ID, gID):
        logger.info("Inserted %s %s into group_members",ID,gID)
        return self.conn.execute("INSERT INTO group_members (g_id,id) VALUES (?, ?);",(gID,ID))

    def get_groups(self,ID):
        logger.info("Selected names from group with ID %s",ID)
        return self.conn.execute("SELECT G.name FROM group_members GM JOIN groups G on GM.g_id=G.g_id WHERE GM.id=?",(ID,)).fetchall()

    def delete_replay(self,ID):
        logger.info("DELETING REPLAY: %s",ID)
        return self.conn.execute("DELETE FROM replays WHERE id=?",(ID,))

    def delete_tag(self,ID,tagname,timestamp):
        logger.info("Deleting tag %s:%s from replay %s",tagname,timestamp,ID)
        return self.conn.execute("DELETE FROM tags WHERE id=? AND tagname=? AND timestamp=?",(ID,tagname,timestamp))
    def delete_from_group(self, ID, groupname):
        logger.info("Deleting replay %s from group %s",ID,groupname)
        group_id = self.conn.execute("SELECT g_id FROM groups WHERE name=?;",(groupname,)).fetchone()[0]
        return self.conn.execute("DELETE FROM group_members WHERE id=? and g_id=?;",(ID,group_id))

    def get_all(self, table,orderBy=None):
        """Get all the rows from specified table"""
        table = clean(table)
        query = "SELECT * FROM "+table
        if orderBy:
            query += " ORDER BY "+orderBy
        logger.debug(query)
        return self.conn.execute(query).fetchall()

    def get_all_where(self,table,**kw):
        """Get all the rows from specified table where all conditions are satisfied
            conditions are passed as cond1=(cmp,var1),cond2=(cmp,var2)
        """

        table = clean(table)
        for k in kw.keys():
            if len(kw[k]) != 2:
                print "Is keyword a tuple?"

            if(type(kw[k][1]) == str):
                kw[k] = (kw[k][0],clean(kw[k][1]))

        logger.debug("%s",kw)
        where_clause = " AND ".join([" %s %s :%s" % (key,kw[key][0],key) for key in kw.keys()])
        kw = {k:v[1] for (k,v) in kw.items()}
        logger.info("SELECT * FROM "+table+" WHERE "+where_clause)
        # print "allw kws: ",kw
        return self.conn.execute("SELECT * FROM "+table+" WHERE "+where_clause,kw).fetchall()

    def filter_replays(self,replayfilters={},tagfilters={},playerfilters={},groupfilters={}):
        print replayfilters,tagfilters,playerfilters,groupfilters
        query = "SELECT * FROM replays R " 
        if replayfilters:
            replay_where = self.get_where_clause("R",replayfilters)
            query += "where " + replay_where
        else:
            query += "where 1 "

        if tagfilters:
            tag_where = self.get_where_clause("T",tagfilters)
            tag_select = "SELECT * FROM tags T where R.id = T.id AND " + tag_where
            query += " AND EXISTS("+tag_select+")"

        if playerfilters:
            player_where = self.get_where_clause("P",playerfilters)
            player_select ="SELECT * from teams P where R.id = P.id AND "+player_where
            query += " AND EXISTS("+player_select+")"

        if groupfilters:
            group_where = self.get_where_clause("G",groupfilters)
            group_select = "SELECT * FROM groups G inner join group_members GM on G.g_id=GM.g_id WHERE R.id=GM.id AND "+group_where
            query += " AND EXISTS("+group_select+")"

        kw = combine_dicts(replayfilters,tagfilters,playerfilters,groupfilters)

        kw = {k:v[1] for (k,v) in kw.items()}

        logger.debug("query: %s kws: %s ",query,kw)
        return self.conn.execute(query,kw).fetchall()

        "SELECT * FROM replays R WHERE <replayfilters>  \
        AND EXISTS (SELECT T.id FROM tags T WHERE <tagfilters>) \
        AND EXISTS (SELECT P.id FROM teams P WHERE <playerfilters>\
        AND EXISTS (SELECT G.id FROM (SELECT * from group g inner join group_members gm on g.g_id=gm.g_id AND g.name=groupname"
    
    def close(self):   
        self.conn.close()


    def __enter__(self):
        return self

    def __exit__(self ,type_, value, traceback):
        logger.info("with __exit__ values: %s %s %s", type_,value,traceback)
        if type_ or traceback:
            self.conn.rollback()
            logger.info("Rolled back")
        else:
            self.conn.commit()
            logger.info("Committed!")
        self.close()

    def get_where_clause(self,table_alias,kw):
        return " AND ".join([table_alias+".%s %s :%s" % (key,kw[key][0],key) for key in kw.keys()])

    def dprint(self,msg,*arg):
        if self.debug:
            print msg % arg

    def add_import(self,importdata):
        c = self.add_replay(importdata['filename'],importdata['name'],importdata['map'],importdata['date'])
        rid = c.lastrowid

        for t in importdata['teams']:
            self.add_team(rid,*t)
        for n in importdata['notes']:
            self.add_note(rid, n[0])
        for g in importdata['groups']:
            try:
                self.add_group(g[0])
            except sqlite3.IntegrityError:
                pass #Group already existed
            self.add_replay_to_group(rid, self.get_all_where("groups",name=("=",g[0]))[0][0])
        for t in importdata['tags']:
            self.add_tag(rid,*t)







if __name__ == '__main__':
    with DB_Manager(debug=True) as mann:
        # print mann.get_all("replays")
        # print mann.get_all_where("replays",filename=("=","hurr"))
        # print mann.get_all_where("replays",map=("=","Durrtown"))
        # print mann.get_all_where("replays",id=(">",1))
        mann.get_all_where("replays",id=(">",1),map=("=","DFH Stadium"))
        print mann.filter_replays(replayfilters=dict(map=("=","DFH Stadium")),tagfilters=dict(),playerfilters=dict(playername=("=","C-Block")),groupfilters=dict())
        print mann.replay_exists("2J8GR5U4AXHFEPNQW9DZK371T6Y0BOMS")
        print mann.replay_exists("2J8GR5U4AXHFEPNQW9")
