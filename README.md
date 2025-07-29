# pyclock.py

## is a large LCD alarm clock

  This is an alarm clock that is capable of waking the system
  from sleep before the alarm occurs.

  The control of the RTC needs root, so start this as a suid program.

        chmod u+s pyclock.py

  Other possible arrangement is giving your user access to the RTC by
allowing your user to control /dev/rtc0 (or whatever your system is configured as)

  Notes:

  Starting as root may be challenging, as most subsystems resist running as root.
  For instance, sound may not play, the graphical system may not work as intended.
  This is actually a good thing, protecting system integrity.

  The LCD is a crude version of the one I created a decade ago.

## Screen shot:

![Screen Shot of DIFF](screen.png)

## Setting alarm:

  Click on the mini button at the lower right corner region titled
  "Set Alarm".

 The LCD changes color, and one can drag up or down on the digits to change time.
 When done, click on the 'Set Alarm' button again.

 # Testing:

  Set alarm 3 minutes rom now. Put the system to sleep with the 'Sleep' or 'Hybernate'
 button.  The system wakes 30 seconds before the alarm time is due.

 # Tech

   On linux, the RTC operates on UTC standard time. The values are translated
back and forth between RTS and LOCAL time transparently. However, this
might cause copmlacation at dual boot with windows etc ...

// EOF
