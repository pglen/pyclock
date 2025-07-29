#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings

from pymenu import  *
from pgui import  *

from pyvguicom import pgutils

#print(os.path.dirname(pgutils.__file__))
sys.path.append(os.path.dirname(pgutils.__file__))
from pyvguicom import pggui

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

MOUSE_DELTA = 10

# ------------------------------------------------------------------------
#    -0-   |   -o-     ---      -2-      -3-      ---
#   6   1  |  o   o   |   1    |   2    |   3    4   4
#    -5-   |   ---     ---      -2-      -3-      -4-
#   4   2  |  o   o   |   1    2   |    |   3    |   4
#    -3-   |   -o-     ---      -2-      -3-      ---

num_0 = 1, 1, 1, 1, 1, 0, 1
num_1 = 0, 1, 1, 0, 0, 0, 0
num_2 = 1, 1, 0, 1, 1, 1, 0
num_3 = 1, 1, 1, 1, 0, 1, 0
num_4 = 0, 1, 1, 0, 0, 1, 1

#     -0-   |    -5-    ---      -o-      -o-      -9-
#    6   1  |   5   |  6   |    |   o    o   o    9   9
#     -5-   |    -5-    -6-      ---      -o-      -9-
#    4   2  |   |   5  6   6    |   o    o   o    |   9
#     -3-   |    -5-    -6-      ---      -o-      ---

num_5 = 1, 0, 1, 1, 0, 1, 1
num_6 = 0, 0, 1, 1, 1, 1, 1
num_7 = 1, 1, 1, 0, 0, 0, 0
num_8 = 1, 1, 1, 1, 1, 1, 1
num_9 = 1, 1, 1, 0, 0, 1, 1

#    -a-      ---      -c-      ---      -e-      -f-
#   a   a    b   |    c   |    |   d    e   |    f   |
#    -a-      -b-      ---      -d-      -e-      -f-
#   a   a    b   b    c   |    d   d    e   |    f   |
#    ---      -b-      -c-      -d-      -e-      ---

num_a = 1, 1, 1, 0, 1, 1, 1
num_b = 0, 0, 1, 1, 1, 1, 1
num_c = 1, 0, 0, 1, 1, 0, 1
num_d = 0, 1, 1, 1, 1, 1, 0
num_e = 1, 0, 0, 1, 1, 1, 1
num_f = 1, 0, 0, 0, 1, 1, 1

num_blank = 0, 0, 0, 0, 0, 0, 0

numarr = (num_0, num_1, num_2, num_3, num_4,
            num_5, num_6, num_7, num_8, num_9,
                num_a, num_b, num_c, num_d, num_e, num_f, )


class LCD_dots(Gtk.DrawingArea):
    def __init__(self, conf = None):

        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        self.set_size_request(12, 12)
        self.border = 2
        self.connect("draw", self.draw_event)

        self.paintbg = 0
        self.bg   = (.0, .0, .0)
        self.fg   = (1, 1, 1)
        self.off  = (.7, .7, .7)
        self._val = -1

    def onoff(self, flag):
        self._val = flag
        self.queue_draw()

    def hide_dot(self):
        self._val = -1
        self.queue_draw()

    def draw_event(self, pdoc, cr):

        #cr.set_source_rgba(0, 0, 0, .3)
        #cr.paint()

        rect = self.get_allocation()
        xpitch = max(rect.width / 8, 4);
        ypitch = max(rect.height / 8, 4);

        #print ("draw called",  rect.width, rect.height)
        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        bg_color = ctx.get_background_color(Gtk.StateFlags.NORMAL)

        # Paint white, ignore system BG
        #cr.set_source_rgba(*self.bg)

        # Background
        if self.paintbg:
            cr.rectangle( 0, 0, rect.width, rect.height);
            cr.fill()

        if self._val < 0:
            cr.set_source_rgba(*bg_color)
        elif self._val == 2:
            cr.set_source_rgba(*self.off)
        elif self._val == 1:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.bg)

        cr.rectangle(self.border, 2 * ypitch + self.border,
                           rect.width - 2 * self.border,
                                ypitch)

        cr.rectangle(self.border, 4.5 * ypitch + self.border,
                           rect.width - 2 * self.border,
                                ypitch)
        cr.fill()

class LCD7(Gtk.DrawingArea):

    def __init__(self, conf = None):

        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        self.set_size_request(20, 20)
        self.border = 2
        self.mode = 1
        self.connect("draw", self.draw_event)
        self.connect("motion-notify-event", self.motion)
        self.paintbg = 0
        self.bg = (.9, .9, .9, 1)
        self.fg = (.0, .0, .0, 1)
        self.off = None #(1, 1, 1)
        self._val = num_blank
        self._num = 0;
        #self.set_app_paintable(True)
        self.setala = False
        self.old_pos = 0
        self.uplink = None
        self.uplink_lim = 10

        self.set_events(  Gdk.EventMask.POINTER_MOTION_MASK |
                            Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                            Gdk.EventMask.BUTTON_PRESS_MASK |
                            Gdk.EventMask.BUTTON_RELEASE_MASK |
                            Gdk.EventMask.KEY_PRESS_MASK |
                            Gdk.EventMask.KEY_RELEASE_MASK |
                            Gdk.EventMask.FOCUS_CHANGE_MASK )

    def motion(self, widg, event):
        if not self.setala:
            return
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            #print("motion", widg, eventx.state)
            #print("delta",  self.old_pos - event.y)

            if self.old_pos - event.y > MOUSE_DELTA:
                if self._num >= self.uplink_lim - 1:
                    if self.uplink:
                        self.uplink.set_num((self.uplink._num + 1) )
                    self._num = 0
                else:
                    self._num += 1
                self.set_num(self._num)
                self.old_pos = event.y
            elif self.old_pos - event.y < -MOUSE_DELTA:
                if self._num <= 0:
                    if self.uplink:
                        self.uplink.set_num(self.uplink._num - 1)
                if (self._num <=  0):
                    self._num = self.uplink_lim -1
                else:
                    self._num -= 1
                self.set_num(self._num)
                self.old_pos = event.y
        else:
            #print("motion pos", widg, eventx.state)
            self.old_pos = event.y

    def set_num(self, num):
        self._num = num %  (self.uplink_lim )
        self._val = numarr[num %  (self.uplink_lim)]
        self.queue_draw()

    def draw_event(self, pdoc, cr):
        if self.mode == 0:
            self.mode_nul(cr)
        elif self.mode == 1:
            self.mode_one(cr)
        else:
            self.mode_nul(cr)

    def mode_one(self, cr):
        rect = self.get_allocation()
        xpitch = rect.width / 6;
        ypitch = rect.height / 6;
        #xpitch = max(rect.width / 8, 4);
        #ypitch = max(rect.height / 8, 4);

        #print ("draw called",  rect.width, rect.height)
        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        if not self.off:
            bg_color = ctx.get_background_color(Gtk.StateFlags.NORMAL)
            self.off = bg_color

        # Paint white, ignore system BG
        # Background
        if self.paintbg:
            cr.set_source_rgba(*self.bg)
            cr.rectangle( 0, 0, rect.width, rect.height);
            cr.fill()

        # ---- top
        if self._val[0]:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.off)

        cr.set_source_rgba(*self.fg)
        #    -0-   |
        #   6   1  |
        #    -5-   |
        #   4   2  |
        #    -3-   |
        if self._val[0]:
            self.draw_hor(cr, 2 * self.border, self.border,
                   int(ypitch),
                      rect.width - 2 * self.border,
                         rect.width - int(ypitch) - 2 * self.border)
        if self._val[3]:
            self.draw_hor2(cr, self.border, rect.height - ypitch - self.border,
                    int(ypitch),
                       rect.width - 2 * self.border,
                          rect.width - int(ypitch) - 2 * self.border)
        if self._val[5]:
            self.draw_hor3(cr, 2 * self.border,
                    rect.height / 2 - ypitch / 2,
                        int(ypitch),
                            rect.width - self.border,
                            rect.width - int(ypitch) - self.border)
        #    -0-   |
        #   6   1  |
        #    -5-   |
        #   4   2  |
        #    -3-   |
        if self._val[6]:
            self.draw_ver(cr, self.border, self.border,
                       int(ypitch) -  self.border,
                       rect.height//2 - self.border,
                          rect.height//2 - int(ypitch) - self.border)

        if self._val[4]:
            self.draw_ver2(cr, self.border, rect.height//2 + self.border,
                        int(ypitch) - self.border,
                        rect.height//2 - 2 * self.border,
                        rect.height//2 - int(ypitch)- 2 * self.border)
        if self._val[1]:
            self.draw_ver3(cr, rect.width - ypitch + self.border,
                    int(ypitch) + 2 * self.border,
                    int(ypitch) - self.border,
                    int(18 * rect.height/32 - 2 * ypitch),
                    int(18 * rect.height/32 - ypitch) )

        if self._val[2]:
            self.draw_ver4(cr, int(rect.width - ypitch) + self.border,
                    18 * rect.height//32 + 2 * self.border,
                    int(ypitch),
                    19 * rect.height//32 - 2 * ypitch ,
                    19 * rect.height//32 - ypitch )
        cr.stroke()

    def draw_hor(self, cr, x1, y1, hh1, ww1, ww2):

        try:
            delta = ((ww1 - ww2) / hh1 )
            for aa in range(hh1):
                cr.move_to(int(x1 + aa * delta), y1 + aa )
                cr.line_to(int(x1 + ww1 - aa * delta), y1 + aa )
        except:
            pass

    def draw_hor2(self, cr, x1, y1, hh1, ww1, ww2):

        try:
            delta = ((ww1 - ww2) / hh1 )
            for aa in range(hh1):
                cr.move_to(int(x1 + aa * delta), y1 + hh1 - aa )
                cr.line_to(int(x1 + ww1 - aa * delta), y1 +hh1 - aa )
        except:
            pass

    def draw_hor3(self, cr, x1, y1, hh1, ww1, ww2):

        try:
            delta = ((ww1 - ww2) / hh1 ) * 2
            for aa in range(hh1//2):
                cr.move_to(int(x1 + aa * delta), y1 + hh1//2 - aa )
                cr.line_to(int(x1 + ww1 - aa * delta), y1 + hh1//2 - aa )
            for aa  in range(hh1//2):
                cr.move_to(int(x1 + aa * delta), hh1//2 + y1 + aa + 2)
                cr.line_to(int(x1 + ww1 - aa * delta), hh1//2 + y1 + aa +2)
        except:
            pass
    #  x1,y1
    #    |
    #    | |       hh2
    #    |    hh1
    #    ww1

    def draw_ver(self, cr, x1, y1, ww1, hh1, hh2):
        try:
            delta = ((hh1 - hh2) / ww1)
            for aa in range(ww1):
                cr.move_to(x1 + aa, int(y1 + aa * delta) )
                cr.line_to(x1 + aa, int(y1 + hh1 - aa * delta/2) )
        except:
            pass

    def draw_ver2(self, cr, x1, y1, ww1, hh1, hh2):
        try:
            delta = ((hh1 - hh2) / ww1)
            for aa in range(ww1):
                cr.move_to(x1 + aa, int(y1 + aa * delta/2) )
                cr.line_to(x1 + aa, int(y1 + hh1 - aa * delta) )
        except:
            pass

    def draw_ver3(self, cr, x1, y1, ww1, hh1, hh2):
        try:
            delta = ((hh1 - hh2) / ww1)
            for aa in range(ww1):
                cr.move_to(x1 + aa, y1 + int(aa * delta) )
                cr.line_to(x1 + aa, y1 + hh1 - int(aa * delta/2) )
        except:
            pass

    def draw_ver4(self, cr, x1, y1, ww1, hh1, hh2):
        try:
            delta = ((hh1 - hh2) / ww1)
            for aa in range(ww1):
                cr.move_to(x1 + aa, int(y1 + aa * delta/2) )
                cr.line_to(x1 + aa, int(y1 + hh1 - aa * delta) )
        except:
            pass

    def mode_nul(self, cr):

        rect = self.get_allocation()
        xpitch = rect.width / 8;
        ypitch = rect.height / 8;

        #xpitch = max(rect.width / 8, 8);
        #ypitch = max(rect.height / 8, 8);

        #print ("draw called",  rect.width, rect.height)
        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        bg_color = ctx.get_background_color(Gtk.StateFlags.NORMAL)
        if not self.off:
            self.off = bg_color
        # Paint white, ignore system BG
        cr.set_source_rgba(*self.bg)

        # Background
        if self.paintbg:
            cr.rectangle( 0, 0, rect.width, rect.height);
            cr.fill()

        #  -0-
        # 6   1
        #  -5-
        # 4   2
        #  -3-

        # ---- top
        if self._val[0]:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.off)
        cr.rectangle(self.border, self.border,
                           rect.width - 3 * self.border,
                                ypitch)
        cr.fill()
        # ____  buttom
        if self._val[3]:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.off)
        cr.rectangle(self.border, 7 * ypitch,
                           rect.width - 3 * self.border,
                                8 * ypitch - 2 * self.border)
        cr.fill()

        # | ----- top left
        if self._val[6]:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.off)
        cr.rectangle(self.border, ypitch + 2 * self.border,
                            xpitch - self.border,
                                3 * ypitch - 2 * self.border)
        cr.fill()

        # | ----- buttom left
        if self._val[4]:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.off)
        cr.rectangle(self.border, 4 * ypitch + 2 * self.border,
                            xpitch - self.border,
                                3 * ypitch - 3 * self.border)
        cr.fill()

        # ---- | top right
        if self._val[1]:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.off)

        cr.rectangle(7*xpitch - self.border, ypitch + 2 * self.border,
                            xpitch - self.border,
                                3 * ypitch - 2 * self.border)
        cr.fill()

        # ---- | buttom right
        if self._val[2]:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.off)
        cr.rectangle(7*xpitch - self.border, 4 * ypitch + 2 * self.border,
                            xpitch - self.border,
                                3 * ypitch - 3 * self.border)
        cr.fill()

        # |---- | Middle
        if self._val[5]:
            cr.set_source_rgba(*self.fg)
        else:
            cr.set_source_rgba(*self.off)
        cr.rectangle(xpitch + self.border, 3.5 * ypitch + self.border,
                            6 * xpitch - 3 * self.border,
                                 ypitch + self.border)
        cr.fill()

# EOF
