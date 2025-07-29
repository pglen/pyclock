#!/usr/bin/env python3

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

sys.path.append('pyclocklib')
from pyclocklib.mainwin import  *

from pyvguicom import comline

# ------------------------------------------------------------------------
# Globals

version = "1.00"

# ------------------------------------------------------------------------

def phelp():

    comline.phelplong()
    sys.exit(0)

    #print()
    #print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    #print()
    #print( "Options:    -d level  - Debug level 0-10")
    #print( "            -p        - Port to use (default: 9999)")
    #print( "            -v        - Verbose")
    #print( "            -V        - Version")
    #print( "            -q        - Quiet")
    #print( "            -h        - Help")
    #print()
    #sys.exit(0)
    #

# ------------------------------------------------------------------------
def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function, help
optarr = [\
    ["d:",  "debug=",   "pgdebug",  0,      None,     "Debug level. 0=none 10=noisy. Default: 0" ],
    ["p:",  "port=",    "port",     9999,   None,     "Listen on port. Default: 9999"],
    ["q",   "quiet",    "quiet",    0,      None,     "Quiet. Show less info."],
    ["v",   "verbose",  "verbose",  0,      None,     "Increase verbosity."],
    ["V",   "version",  None,       None,   pversion, "Print Version string."],
    ["h",   "help",     None,       None,   phelp,    "Show Help. (this screen)"],
    ]

#comline.setprog("Usage: template.py [options]")
comline.sethead("Alarm Clock with big LCD")
comline.setargs("[options]")
comline.setfoot("This program with set the RTC wake time as well.")
conf = comline.ConfigLong(optarr)

if __name__ == '__main__':

    global mw
    args = conf.comline(sys.argv[1:])
    mw = MainWin(conf)
    mw.run()
    sys.exit(0)

# EOF