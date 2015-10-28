#!/usr/bin/python2

#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import sys
import re
import os
import replay_parser
reg = re.compile(r"PlayerName.*?StrProperty.*?(\w+)\x00",re.MULTILINE|re.DOTALL)
regd = re.compile(r"(\w+)\x00")


datereg = re.compile("\d{4}-\d\d-\d\d:\d\d-\d\d")#YYYY-MM-DD:HH-MM
VARS = ["TAGame","Replay_Soccar_TA","TeamSize","IntProperty","Team0Score","Team1Score","StrProperty",
"None","frame","Shots","bBot","BoolProperty","Date","Offline","Goals","ArrayProperty",
"PlayerName","PlayerTeam","PlayerStats","Platform","ByteProperty","OnlinePlatform",
"OnlinePlatform_Steam","OnlineID","Team","Assists","Saves","RecordFPS","FloatProperty",
"KeyframeDelay","MaxChannels","MaxReplaySizeMB","OnlinePlatform_Unknown","QWordProperty",
"Score","SWBt","BYCm","NumFrames","NameProperty","Unknown","Name","Dusk","Dawn","day","night","Replay","Soccar","Steam"]
def match(filen):
    with open(filen,'r') as f:
        content = f.read()
        matches = reg.findall(content)
        dumbmatches = regd.findall(content)
        dumbmatches = filter(lambda x:len(x)>1 and x not in VARS and x not in filen,dumbmatches)
        print matches
        print "dumbs, ",dumbmatches
        print datereg.findall(content)


d = "C:/Users/Erik/Documents/My Games/Rocket League/TAGame/Demos/"
par = replay_parser.ReplayParser()
for filename in os.listdir(d):
    print filename
    match(d+filename)
    print par.parse(d+filename)['header']
    print " "