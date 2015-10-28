#!/usr/bin/python2
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import time
import re
import struct
import os
import psycopg2
import sys
import DB_HANDLES

RL_DEMO_PATH = os.environ["userprofile"]+"\Documents\My Games\Rocket League\TAGame\Demos"
def main():

    #Define our connection string
    conn_string = "host='localhost' port='5433' dbname='postgres' user='postgres' password='alpha'"
 
    # print the connection string we will use to connect
    print "Connecting to database\n ->%s" % (conn_string)
 
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
 
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    print "Connected!\n"
    for filename in os.listdir(RL_DEMO_PATH):
        print filename,type(filename)
        cursor.execute("INSERT INTO replays (filename) VALUES (%s)",(filename.split(".")[0],))
    conn.commit()
if __name__ == "__main__":
    main()