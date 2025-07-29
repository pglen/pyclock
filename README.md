# pyclock.py

## is a large LCD alarm clock

  This is an alarm clock that is capable of waking the system
  from sleep before the alarm occurs.

  The control of the RTC needs suid root, so start this as a suid program.

        chmod u+s pyclock.py

  The other possible arrangement is giving your user access to the RTC by
allowing your user to control /dev/rtc0 (or whatever your system is configured as)
(note: udevd makes it harder to accomplish this)

## Setting alarm:

  Click on the mini button at the lower right corner region titled
  "Set Alarm".

 The LCD changes color, and one can drag up or down on the digits to change time.
 When done, click on the 'Set Alarm' button again.

## Screen shot:

![Screen Shot of DIFF](screen.png)

### Notes:

  We recommend suid, because trying to start a GUI program as root may be challenging.
  Most subsystems resist running as root. For instance, sound may not play,
  or the graphical system may not work as intended. This is actually a good thing,
  protecting system integrity.

## Testing:

  Set alarm 3 minutes rom now. Put the system to sleep with the 'Sleep' or 'Suspend' or
  'Hibernate' button.  The system wakes 30 seconds before the alarm time is due.
  Alarm should sound for 5 separate repeats. Click on the "Close Alarm" button to
  stop alarm sound.

 ## Tech

   On linux, the RTC operates on UTC standard time. The values are translated
back and forth between RTC and LOCAL time transparently. However, this
might cause complication at dual boot with windows etc ... This is not a
limitation of pyclock, rather the underlying systems.

 ### Use the source:

  The LCD is a crude version of the one I created a decade ago. Most useful as it
scales nicely and can display hexadecimal digits as well.


// EOF
