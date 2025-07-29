#!/usr/bin/env python

import os, sys, getopt, signal
import random, time

#import gobject, gtk, pango

# ------------------------------------------------------------------------

class MainWin():

    def __init__(self):

        self.window = window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        window.set_title("Template")
        window.set_position(gtk.WIN_POS_CENTER)

        #ic = gtk.Image(); ic.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_BUTTON)
        #window.set_icon(ic.get_pixbuf())

        www = gtk.gdk.screen_width(); hhh = gtk.gdk.screen_height();
        window.set_default_size(www/2, hhh/2)

        window.set_flags(gtk.CAN_FOCUS | gtk.SENSITIVE)

        window.set_events(  gtk.gdk.POINTER_MOTION_MASK |
                            gtk.gdk.POINTER_MOTION_HINT_MASK |
                            gtk.gdk.BUTTON_PRESS_MASK |
                            gtk.gdk.BUTTON_RELEASE_MASK |
                            gtk.gdk.KEY_PRESS_MASK |
                            gtk.gdk.KEY_RELEASE_MASK |
                            gtk.gdk.FOCUS_CHANGE_MASK )

        window.connect("destroy", self.OnExit)
        window.connect("key-press-event", self.key_press_event)
        window.connect("button-press-event", self.button_press_event)

        try:
            window.set_icon_from_file("icon.png")
        except:
            pass

        vbox = gtk.VBox(); hbox = gtk.HBox()
        lab1 = gtk.Label("");  hbox.pack_start(lab1)

        butt1 = gtk.Button(" _New ")
        #butt1.connect("clicked", self.show_new, window)
        hbox.pack_start(butt1, False)

        butt2 = gtk.Button(" E_xit ")
        butt2.connect("clicked", self.OnExit, window)
        hbox.pack_start(butt2, False)

        lab2 = gtk.Label("");  hbox.pack_start(lab2)
        vbox.pack_start(hbox, False)

        hbox2 = gtk.HBox()

        lab3 = gtk.Label("");  hbox2.pack_start(lab3)

        lab4 = gtk.Label("");  hbox2.pack_start(lab4)
        vbox.pack_start(hbox2, False)
        window.add(vbox)
        window.show_all()

    def  OnExit(self, arg, srg2 = None):
        self.exit_all()

    def exit_all(self):
        gtk.main_quit()

    def key_press_event(self, win, event):
        print ("key_press_event", win, event)
        pass

    def button_press_event(self, win, event):
        print ("key_press_event", win, event)
        pass

# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    gtk.main()







