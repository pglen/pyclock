#!/usr/bin/env python

try:
    from playsound3 import playsound
except:
    def playsound(arg):
        print("Fake playsound")
        #Gdk.beep()
        pass
    #print("No sound subsystem")

def play_sound(sfile = ""):

    if not sfile:
        sfile = "/usr/share/sounds/freedesktop/stereo/complete.oga"

    global sound
    sound = playsound(sfile, block=False)

def stop_sound(sfile = ""):
    global sound
    sound.stop()

# EOF
