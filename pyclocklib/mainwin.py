#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings
import datetime, subprocess

mydir = os.path.dirname(__file__)
#print("adding:", mydir)
sys.path.append(os.path.dirname(__file__))

gongs   = os.path.join(mydir, "gong.ogg")
alarms  = os.path.join(mydir, "alarm.oga")
askrtc  =  os.path.join(mydir, "askrtc.sh")
iconf   =  os.path.join(mydir, "pyclock.png")

from pymenu import  *
from pgui import  *

from pyvguicom import pgutils
#print(os.path.dirname(pgutils.__file__))
sys.path.append(os.path.dirname(pgutils.__file__))

from pyvguicom import pggui
sys.path.append(pggui.__file__)
from pyvguicom import pgbutt

import lcd
import soundx
import alwin
import pgutil

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import cairo

class smallLab(Gtk.Label):

    def __init__(self, text = ""):
        Gtk.Label.__init__(self)
        font = "Sans 10"
        self.override_font(Pango.FontDescription(font))
        self.set_text(text)
# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self, adt, conf = None):

        self.adt = adt
        self.alcnt = 0
        self.aloff = False
        self.cnt = 0
        self.conf = conf
        self.stattime =  0
        self.setala = False
        self.alarm = None
        self.alarm2 = None
        self.alwinx = None

        if self.conf.pgdebug:
            print("Starting pyclock ...")
        #print("Conf: deb", conf.pgdebug, "verb", conf.verbose)

        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL)
        #Gtk.Window.__init__(self, Gtk.WindowType.POPUP)
        self.set_decorated(False)
        #Gtk.register_stock_icons()
        #self.set_title("PyClock")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        #ic = Gtk.Image(); ic.new_from_file(iconf)
        #set_default_icon(ic.get_pixbuf())

        self.set_default_icon_from_file(iconf)

        www = Gdk.Screen.width(); hhh = Gdk.Screen.height();

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print( disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();

        #self.set_app_paintable(True)

        #if www / hhh > 2:
        #    self.set_default_size(3*www/8, 7*hhh/8)
        #else:
        self.set_default_size(5*www/8, 3*hhh/8)

        '''
        self.set_events(  Gdk.POINTER_MOTION_MASK |
                            Gdk.POINTER_MOTION_HINT_MASK |
                            Gdk.BUTTON_PRESS_MASK |
                            Gdk.BUTTON_RELEASE_MASK |
                            Gdk.KEY_PRESS_MASK |
                            Gdk.KEY_RELEASE_MASK |
                            Gdk.FOCUS_CHANGE_MASK )
        '''
        self.connect("destroy", self.OnExit)
        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.button_press_event)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        vbox = Gtk.VBox();

        merge = Gtk.UIManager()
        #self.mywin.set_data("ui-manager", merge)

        aa = create_action_group(self)
        merge.insert_action_group(aa, 0)
        self.add_accel_group(merge.get_accel_group())

        merge_id = merge.new_merge_id()

        try:
            mergeid = merge.add_ui_from_string(ui_info)
        except GLib.GError as msg:
            print("Building menus failed: %s" % msg)

        #self.mbar = merge.get_widget("/MenuBar")
        #self.mbar.show()

        self.tbar = merge.get_widget("/ToolBar");
        #self.tbar.show()

        bbox = Gtk.VBox()
        #bbox.pack_start(self.mbar, 0, 0, 0)
        #bbox.pack_start(self.tbar, 0, 0, 0)
        vbox.pack_start(bbox, 0, 0, 0)

        hbox2 = Gtk.HBox()
        #lab3 = Gtk.Label(label="  ");   hbox2.pack_start(lab3,  1, 1, 0)
        #lab4 = Gtk.Label(label="Top");  hbox2.pack_start(lab4, 0, 0, 0)
        #lab5 = Gtk.Label(label="  ");   hbox2.pack_start(lab5, 1, 1, 0)

        vbox.pack_start(hbox2, 0, 0, 4)

        self.hbox3 = Gtk.HBox()
        self.hbox3.pack_start(Gtk.Label(label=" "), False, False, 2)

        self.lcdh0 = lcd.LCD7()
        self.lcdh0.uplink_lim = 3
        self.hbox3.pack_start(self.lcdh0, True, True, 2)

        self.lcdh1 = lcd.LCD7()
        self.lcdh1.uplink = self.lcdh0
        self.hbox3.pack_start(self.lcdh1, True, True, 2)

        self.dotsh = lcd.LCD_dots()
        self.hbox3.pack_start(self.dotsh, False, False, 4)

        self.lcdm0 = lcd.LCD7()
        self.lcdm0.uplink_lim = 6
        self.hbox3.pack_start(self.lcdm0, True, True, 2)

        self.lcdm1 = lcd.LCD7()
        self.lcdm1.uplink = self.lcdm0
        self.hbox3.pack_start(self.lcdm1, True, True, 2)

        self.dotsm = lcd.LCD_dots()
        self.hbox3.pack_start(self.dotsm, False, False, 4)

        self.lcds0 = lcd.LCD7()
        self.lcds0.uplink_lim = 6
        self.hbox3.pack_start(self.lcds0, True, True, 2)

        self.lcds1 = lcd.LCD7()
        self.lcds1.uplink = self.lcds0
        self.hbox3.pack_start(self.lcds1, True, True, 2)

        self.hbox3.pack_start(Gtk.Label(label=" "), False, False, 2)

        # Array of controls
        self.ctrarr = (self.lcdh0, self.lcdh1,
                        self.lcdm0, self.lcdm1,
                            self.lcds0, self.lcds1, )
        vbox.pack_start(self.hbox3, True, True, 2)

        hbox2a = Gtk.HBox()
        lab3a = Gtk.Label(label="  ");    hbox2a.pack_start(lab3a, 1, 1, 0)
        lab4a = Gtk.Label(label="Butt");  hbox2a.pack_start(lab4a, 0, 0, 0)
        lab5a = Gtk.Label(label="  ");    hbox2a.pack_start(lab5a, 1, 1, 0)

        #vbox.pack_start(hbox2a, 1, 1, 0)

        # buttom row
        hbox4 = Gtk.HBox()
        hbox4.pack_start(smallLab("  Alarm:  "), 0, 0, 0)
        self.alarmlab = smallLab("None");
        hbox4.pack_start(self.alarmlab, 0, 0, 0)
        hbox4.pack_start(smallLab("  "), 0, 0, 0)
        self.status = smallLab("  ")
        hbox4.pack_start(self.status, 1, 1, 0)
        self.status.set_xalign(0)

        butt3 = pgbutt.smallbutt("  _Set Alarm  ", self.set_ala,
                        "Set alarm (Alt-S). Click again to ack.")
        hbox4.pack_start(butt3, False, 0, 2)

        butt4 = pgbutt.smallbutt("  E_xit  ", self.OnExit,
                        "Exit (Alt-X) program. RTC Wake stays active.")
        hbox4.pack_start(butt4, False, 0, 2)

        lab2b = Gtk.Label(label="  ");  hbox4.pack_start(lab2b, 0, 0, 0)

        vbox.pack_start(hbox4, False, False, 4)
        self.set_opacity(.5)
        self.add(vbox)
        self.show_all()

        #self.set_app_paintable(True)
        #self.set_opacity(.6)
        #self.connect("draw", self.area_draw)
        #print("ccc", self.is_composited() )

        GLib.timeout_add(200, self.load)
        # Show one before timer
        self.timer_tick()
        GLib.timeout_add(1000, self.timer_tick)

    def set_sec_check(self, butt):
        #print(butt)
        if butt.get_active():
            self.dotsm.show()
            self.lcds0.show()
            self.lcds1.show()
        else:
            self.dotsm.hide()
            self.lcds0.hide()
            self.lcds1.hide()

    def area_draw(self, widget, cr):
        cr.set_source_rgba(.0, .0, .0, 0.0)
        #cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_operator(cairo.OPERATOR_OVER)
        #cr.paint()

    def  OnExit(self, arg, srg2 = None):
        self.exit_all()

    def exit_all(self):
        Gtk.main_quit()

    def key_press_event(self, win, event):
        #print( "key_press_event", win, event)
        pass

    def set_ala(self, butt):
        #print("set_ala", butt)
        self._set_ala()

    def _set_ala(self, fromcom = False):
        if self.setala:
            dt2 = None
            dt = datetime.datetime.now()
            try:
                if fromcom:
                    dt2 = fromcom
                else:
                    hhh = self.lcdh0._num * 10 + self.lcdh1._num
                    mmm = self.lcdm0._num * 10 + self.lcdm1._num
                    sss =  self.lcds0._num * 10 + self.lcds1._num
                    ddd = datetime.date(dt.year, dt.month, dt.day)
                    ttt = datetime.time(hhh, mmm, sss)
                    dt2 = datetime.datetime.combine(ddd, ttt)
                if dt2 < dt:
                    pgutil.xmessage("Alarm time extended to tomarrow.")
                    dt2 += datetime.timedelta(hours=24)
            except:
                print(sys.exc_info())
                utils.xmessage("Invalid Date / Time", sys.exc_info()[1])
                return
            self.setala = False
            fg = 0, 0, 0
            ddd = (dt2-dt)
            self.set_status( \
                "Alarm Set to: %d:%d:%d (h:m:s) from now." % \
                    (ddd.total_seconds() // 3600,
                        (ddd.total_seconds() / 60) % 60,
                            (ddd.total_seconds() % 60 ) ))

            #self.alarmlab.set_text("%02d:%02d:%02d" % (hhh, mmm, sss))
            self.alarmlab.set_text("%s" % (dt2))
            self.alarm = dt2
            self.alcnt = 0
            self.set_rtc(self.alarm)
        else:
            self.setala = True
            self.dotsh.onoff(2)
            self.dotsm.onoff(2)
            if self.alarm:
                self.lcds0.set_num(self.alarm.second // 10)
                self.lcds1.set_num(self.alarm.second % 10)
                self.lcdm0.set_num(self.alarm.minute // 10)
                self.lcdm1.set_num(self.alarm.minute % 10)
                self.lcdh0.set_num(self.alarm.hour // 10)
                self.lcdh1.set_num(self.alarm.hour % 10)
            else:
                self.lcds0.set_num(0)
                self.lcds1.set_num(0)
            fg = 0, 0, 5
            self.set_status("Set alarm dragging mouse on digits")

        for aa in self.ctrarr:
            aa.fg = fg
            aa.setala = self.setala
            aa.queue_draw()

    def set_rtc(self, datex = None):

        if not datex:
            datex = datetime.datetime.now() + 60

        # set RTC
        try:
            rtime = int(datex.timestamp() - 30)
            arg = ["sudo", "rtcwake",  "-m",  "no", "-t", str(rtime), "&", ]
            #print("arg:", arg)
            subprocess.call(arg)
        except:
            pass
        #print("After: ", )

    def button_press_event(self, win, event):
        #print( "button_press_event", win, event)
        pass

    def activate_action(self, action):

        #dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
        #    Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE,
        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        #dialog.connect ("response", lambda d, r: d.destroy())
        #dialog.show()

        warnings.simplefilter("ignore")
        strx = action.get_name()
        warnings.simplefilter("default")

        print ("activate_action", strx)

    def activate_quit(self, action):
        print( "activate_quit called")
        self.OnExit(False)

    def activate_exit(self, action):
        print( "activate_exit called" )
        self.OnExit(False)

    def activate_about(self, action):
        print( "activate_about called")
        pass

    def load(self):

        #print("Called load")

        #self.set_status("Status text for load")
        soundx.play_sound(gongs)

        if self.adt:
            #print("adt:", self.adt)
            self.setala = True
            self._set_ala(self.adt)

        # Test items
        #self.set_rtc(datetime.datetime.now())
        #dt = datetime.datetime.now()
        #alwin.AlWin(dt)

    def callb(self):
        print("Close callback")
        soundx.stop_sound()
        self.aloff = True

    def timer_sound(self):
        if self.conf.pgdebug:
            print("timer_sound: alwinx", self.alwinx, self.alcnt)

        if not self.aloff:
            soundx.play_sound(alarms)
            if self.alcnt < 5:
                GLib.timeout_add(10000, self.timer_sound)
                self.alcnt += 1
            else:
                self.aloff = True
                self.alarmlab.set_text("")
        else:
            self.alarmlab.set_text("")

    def timer_alarm(self):
        #print("Alarm", self.alarm2)
        self.alwinx = alwin.AlWin(self.alarm2, self.callb)
        self.alarmlab.set_text("Alert in progress ...")
        #print("alwinx", self.alwinx)

    def timer_tick(self):
        try:
            #print("Called timer_tick", self.cnt % 16)
            ttt = datetime.datetime.now()
            if not self.setala:
                base = 10
                self.cnt += 1
                self.lcdh0.set_num((ttt.hour // base) % base)
                self.lcdh1.set_num((ttt.hour) % base)
                self.lcdm0.set_num((ttt.minute // base) % base)
                self.lcdm1.set_num((ttt.minute) % base)
                self.lcds0.set_num((ttt.second // base) % base)
                self.lcds1.set_num(ttt.second % base)

                # Blink
                if ttt.second % 2:
                    self.dotsh.onoff(1)
                    self.dotsm.onoff(1)
                else:
                    self.dotsh.onoff(0)
                    self.dotsm.onoff(0)

                # Alarm time
                if self.alarm:
                    if self.alarm <= ttt:
                        #print("Action ala:", self.alarm,
                        #        "now:",ttt)
                        self.alarm2 = self.alarm
                        self.alarm = None
                        GLib.timeout_add(300, self.timer_sound)
                        GLib.timeout_add(200, self.timer_alarm)

            if self.stattime == 1:
                self.status.set_text("")
            if self.stattime:
                self.stattime -= 1
        except:
            print("Exc in timer_tick", sys.exc_info())
        return True

    def set_status(self, txt):
        self.status.set_text(txt)
        self.stattime = 1 + len(txt) // 4

    def run(self):
        Gtk.main()

# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    mainwin.run()

# EOF