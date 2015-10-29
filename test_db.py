import sqlite3
import sys
import random as rnd
import db_manager

#Why have a couple of names when you can have all?
names = ["Armstrong", "Bandit", "Beast", "Boomer",
 "Buzz", "Casper", "Caveman", "C-Block",
  "Centice", "Chipper", "Cougar", "Dude",
   "Foamer", "Fury", "Gerwin", "Goose", "Heater",
    "Hollywood", "Hound", "Iceman", "Imp", "Jester",
     "JM", "Junker", "Khan", "Maverick", "Middy", "Merlin",
      "Mountain", "Myrtle", "Outlaw", "Poncho", "Rainmaker",
       "Raja", "Rex", "Roundhouse", "Sabretooth",
 "Saltie", "Samara", "Scout", "Shepard", "Slider", "Squall",
  "Sticks", "Stinger", "Storm", "Sundown", "Sultan", "Swabbie", "Tusk",
   "Tex", "Viper", "Wolfman", "Yuri"]

def randplayerlist(ID):
    global names
    playercount = rnd.choice([2,4,6,8])
    pnames = rnd.sample(names,playercount)
    l = []
    for i in range(0,playercount):
        team = 0 if i < playercount/2 else 1
        l.append( (ID,pnames[i],team,rnd.randint(0,5),rnd.randint(0,12)) )
    return l


def populate_test(loc=":memory:"):
    if loc == ":memory:":
        import setup
        conn = setup.initdb(":memory:")
    else:
        conn = sqlite3.connect(loc)

    conn.execute("PRAGMA foreign_keys = ON")
    replay_insert = "INSERT INTO replays (filename,name,map,datetime) VALUES (?,?,?,?)"
    team_insert = "INSERT INTO teams (id,playername,team,goals,saves) VALUES (?,?,?,?,?)"
    with conn:
        
        c = conn.execute(replay_insert, ("4DF098EF49BE8E3FA65014BA9DE39DAB","Big Tourny 1:1","Utopia Stadium","2015-10-20:22:49"))
        i = c.lastrowid
        conn.executemany(team_insert, randplayerlist(i))

        c = conn.execute("INSERT INTO replays (filename,name,map,datetime) VALUES (?,?,?,?)",
            ("297C8C31452A4D33E9EF5A92DCBF3A1A","Big Tourny 1:2","Urban Central","2015-10-10:21:49"))
        i = c.lastrowid
        conn.executemany(team_insert, randplayerlist(i))

        c = conn.execute("INSERT INTO replays (filename,name,map,datetime) VALUES (?,?,?,?)",
            ("E52660E945D0F3EBFB671D9B82D8CC54","Big Tourny 1:3","DFH Stadium","2015-10-23:12:45"))
        i = c.lastrowid
        conn.executemany(team_insert, randplayerlist(i))

        c = conn.execute("INSERT INTO replays (filename,name,map,datetime) VALUES (?,?,?,?)",
            ("CF4544E24B3DB36C5186EE961C7BE2FF","Big Tourny 1:4","Utopia Stadium","2015-08-20:22:49"))
        i = c.lastrowid
        conn.executemany(team_insert, randplayerlist(i))

        c = conn.execute("INSERT INTO replays (filename,name,map,datetime) VALUES (?,?,?,?)",
            ("CE13707C4FBF32DFDC6D61821820458E","Big Tourny 1:5","Beckwith Park","2015-10-20:22:49"))
        i = c.lastrowid
        conn.executemany(team_insert, randplayerlist(i))

        c = conn.execute("INSERT INTO replays (filename,name,map,datetime) VALUES (?,?,?,?)",
            ("9051A33B48E8AE4A2537A9B7B4038BA9","Big Tourny 1:6","Utopia Stadium","2015-02-20:22:49"))
        i = c.lastrowid
        conn.executemany(team_insert, randplayerlist(i))
    mann = db_manager.DB_Manager()
    mann.conn.close()
    mann.conn = conn
    return mann