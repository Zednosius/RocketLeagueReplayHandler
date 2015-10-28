#!/usr/bin/python2
import psycopg2
import sys
import DB_HANDLES

def initdb():
    #Define our connection string
    conn_string = "host='localhost' port='5433' dbname='postgres' user='postgres' password='alpha'"
 
    # print the connection string we will use to connect
    print "Connecting to database\n ->%s" % (conn_string)
 
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
 
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()

    #ID; FILENAME; NAME; MAP;
    cursor.execute("CREATE TABLE replays (id serial PRIMARY KEY,filename varchar(64),name text,map text,pdate date;ptime time;)")
    
    #ID(fk); TEAM; PLAYERCOUNT; GOALS;  (information about a team in a match)
    cursor.execute("CREATE TABLE match_data (id integer REFERENCES replays ON DELETE CASCADE, team integer, playercount integer, goals integer, saves integer)")
    
    #ID(fk);TEAM; PLAYERNAME; GOALS; SAVES; (information about a player in a match)
    cursor.execute("CREATE TABLE teams (id integer REFERENCES replays ON DELETE CASCADE, team integer, playername text, goals integer, saves integer);")
    
    #ID(fk);TAGNAME;TIMESTAMP; (User created time tags for a match)
    cursor.execute("CREATE TABLE tags (id integer REFERENCES replays ON DELETE CASCADE, tagname text, timestamp integer);")
    
    #ID(fk); NOTE; (Other notes that doesn't have a timestamp)
    cursor.execute("CREATE TABLE notes (id integer REFERENCES replays ON DELETE CASCADE, note text;)")
    
    #ID;NAME; (For grouping a set of replays together) 
    cursor.execute("CREATE TABLE groups (g_id serial PRIMARY KEY; name text);")

    #Many-to-Many relation
    cursor.execute("CREATE TABLE group_members (g_id integer REFERENCES group ON DELETE CASCADE, id integer REFERENCES replays ON DELETE CASCADE;)")

    conn.commit()
    print "Success!"

if __name__ == "__main__":
    if len(sys.argv) == 1:
        initdb()
    else:
        if 