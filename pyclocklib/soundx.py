#!/usr/bin/env python

import threading
#import multiprocessing
#from multiprocessing import Process

try:
    from playsound import playsound
except:
    pass
    def playsound(arg):
        print("Fake playsound")
        #Gdk.beep()
        pass
    #print("No sound subsystem")

lock = threading.Lock()
ttt = None

def _asyncsound(*argx):

    #lock.acquire()
    #print("Thread start", argx)
    #Gdk.beep()
    if not argx[0]:
        argx = \
        ("/usr/share/sounds/freedesktop/stereo/complete.oga", )
    try:
        playsound(argx[0])
    except:
        print("Cannot play sound: '%s'" % argx[0])
        #print("Thread end")

    #lock.release()

def play_sound(sfile = ""):
    global ttt
    ttt = threading.Thread(None, _asyncsound, args=(sfile,))
    #ttt = Process(target=_asyncsound, args=(sfile,))
    ttt.daemon = True
    ttt.start()
    #ttt.join()

def stop_sound(sfile = ""):
    global ttt
    #ttt.terminate()

# EOF
