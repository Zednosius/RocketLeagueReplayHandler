from distutils.core import setup
import py2exe,sys,os
sys.argv.append('py2exe')
setup(
    options = {'py2exe':{'bundle_files':1,'compressed':True,}},
    data_files=['C:\\Python27\\tcl\\tcl8.5\\init.tcl'],
    console=[{'script':'RocketLeagueReplayHandler.py'}],   
    zipfile = None,
    )