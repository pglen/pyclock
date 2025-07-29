#!/usr/bin/env python3

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

class AlWin(Gtk.Window):

    def __init__(self, txt, callb = None):

        Gtk.Window.__init__(self)

        self.callb = callb
        self.frame = Gtk.Frame()
        self.vbox = Gtk.VBox()
        self.butt = Gtk.Button.new_with_mnemonic("  _Close Alert ")
        self.butt.connect("activate", self.exit_win)
        self.butt.connect("pressed", self.exit_win)

        self.hbox = Gtk.HBox()
        self.hbox.pack_start(Gtk.Label(label="   "), 1, 1, 10)
        lab = Gtk.Label(label="Alert")
        fd = Pango.FontDescription("36 Bold")
        lab.modify_font(fd)
        self.hbox.pack_start(lab, 0, 0, 10)
        self.hbox.pack_start(Gtk.Label(label="   "), 1, 1, 10)
        self.vbox.pack_start(self.hbox, 0, 0, 10)

        self.hbox = Gtk.HBox()
        self.hbox.pack_start(Gtk.Label(label="   "), 0, 0, 10)
        self.label = Gtk.Label(label=txt)
        self.hbox.pack_start(self.label, 0, 0, 10)
        self.hbox.pack_start(Gtk.Label(label="   "), 0, 0, 10)

        self.vbox.pack_start(self.hbox, 0, 0, 10)

        self.hbox2 = Gtk.HBox()
        self.hbox2.pack_start(Gtk.Label(label="   "), 0, 0, 2)
        self.hbox2.pack_start(self.butt, 1, 1, 2)
        self.hbox2.pack_start(Gtk.Label(label="   "), 0, 0, 2)
        self.vbox.pack_start(self.hbox2, 1, 1, 10)

        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1)  )
        self.frame.add(self.vbox)
        self.add(self.frame)
        self.set_decorated(False)
        self.show_all()

    def exit_win(self, butt):
        #print("exit_win")
        if self.callb:
            self.callb()
        self.destroy()

# EOF
