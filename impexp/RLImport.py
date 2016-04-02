#!/usr/bin/python2
# -*- coding: utf-8 -*-
#Copyright (C) 2015 Erik Söderberg
#See LICENSE for more information

import zipfile
import json
import rl_paths
from db_manager import * 


def import_zip(path_to_zip, progressQueue=None):
    """
    Imports a zip with jsondata and replays into the application.
    """
    data = {}

    with zipfile.ZipFile(path_to_zip,"r") as fzip:
        with fzip.open("data.json","r") as fdata:
            data = json.loads(fdata.read())
            if progressQueue:
                progressQueue.put("Loaded data")
        for d in data:
            print d
            print "derp"
            fzip.extract(d['filename']+".replay",rl_paths.tracked_folder())
            if progressQueue:
                progressQueue.put("Extracted:" +d['filename'])

            with DB_Manager() as dmann:
                dmann.add_import(d)
                if progressQueue:
                    progressQueue.put("Loaded data from:"+d['filename'])





