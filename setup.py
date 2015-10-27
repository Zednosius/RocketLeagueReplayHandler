#!/usr/bin/python2
import psycopg2
import sys

def main():
    #Define our connection string
    conn_string = "host='localhost' port='5433' dbname='postgres' user='postgres' password='alpha'"
 
    # print the connection string we will use to connect
    print "Connecting to database\n ->%s" % (conn_string)
 
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
 
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()

    #ID; FILENAME; NAME; MAP;
    cursor.execute("CREATE TABLE replays (id serial PRIMARY KEY,filename varchar(64),name text,map text);")
    #ID(fk); TEAM; PLAYERCOUNT; GOALS;  (information about a team in a match)
    cursor.execute("CREATE TABLE match_data (id integer REFERENCES replays ON UPDATE CASCADE ON DELETE CASCADE, team integer, playercount integer, goals integer, saves integer)")
    #ID(fk);TEAM; PLAYERNAME; GOALS; SAVES; (information about a player in a match)
    cursor.execute("CREATE TABLE teams (id integer REFERENCES replays ON UPDATE CASCADE ON DELETE CASCADE, team integer, playername text, goals integer, saves integer);")
    #ID(fk);TAGNAME;TIMESTAMP; (User created tags for a match)
    cursor.execute("CREATE TABLE tags (id integer REFERENCES replays ON UPDATE CASCADE ON DELETE CASCADE, tagname text, timestamp integer);")

    conn.commit()
    print "Success!"
    
if __name__ == "__main__":
    main()