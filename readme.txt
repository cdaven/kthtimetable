KTH TimeTable
===============================================================

Keeps track of your KTH timetable

Main features
-------------

* fetches your timetable from the KTH systems TimeEdit and Daisy (not ISK's server)
* shows your timetable graphically, much like Microsoft Outlook
* exports the timetable to vCalendar and other formats
* lets you choose groups for the courses
* lets you rename the courses

The program stores your timetable locally so that it's always
available to you, even offline. You can easily put your timetable
together from TimeEdit and Daisy, then choose groups and rename
the courses if you like. If you have a PDA or a phone with
calendar you can export your timetable to a file, import it to
Microsoft Outlook, Palm Desktop, Ximian Evolution, J-Pilot or
a similar program, and synchronize with your device.

KTH TimeTable is written in the programming language Python.
It runs on at least Microsoft Windows and Linux (using the GTK
toolkit). It uses the library wxPython for the graphical
interface. It should run on Mac OS as well, but this has not
yet been confirmed.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

This code was abandoned in 2005. Migrated from Sourceforge (CVS) in 2023.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

The timetables are imported directly from the KTH timetable
systems TimeEdit and Daisy. No other systems can be used.

KTH TimeTable is not in any way involved with these systems.
If there are server problems, contact the people responsible.



STARTING THE PROGRAM
===============================================================

Windows
-------

a.) If you downloaded the exe file you just double click on it.

b.) If you downloaded the source code you can double click
on the file "timetable.pyw", or open a command prompt and enter
"python timetable.pyw".


Linux
-----

a1.) Make "timetable.pyw" executable with "chmod +x timetable.pyw".
a2.) Double click on "timetable.pyw".

b.) Open a terminal in X and enter "python timetable.pyw".

c.) In text mode, enter "python timetable.pyw today" to see
the timetable for today.



ABBREVIATIONS AND STUFF
===============================================================

Most event types are not written in full but abbreviated
to save some graphical space.

The abbreviations for English are:

Lect    Lecture
Tut     Tutorial
Lab     Laboratory
Sem     Seminar
WS      Workshop

The abbreviations for Swedish are:

F       F�rel�sning
Lekt    Lektion
�       �vning
Sem     Seminarium
WS      Workshop

Some rooms in the IT University have Swedish names, which
are translated in the program if you have chosen another
language.

Great Hall is "Aulan"
Room X is "Sal X", where X is A, B, C, ...



EXPORT TIMETABLE TO OTHER PROGRAMS
===============================================================

Choose File / Export, then the dates you want to export.
Choose OK and enter the file name you want to export to.

Then choose which application you want to export the timetable
to; Oulook/Palm Desktop, Evolution, or J-Pilot.

The file format used for both Oulook/Palm Desktop and
Evolution is vCalendar. The difference is that Evolution needs
non-ASCII characters to be encoded with UTF-8. (Most PIM
applications should be able to import this file format in
either regular or UTF-8 format.)

Note: vCalendar files can easily be disguised as iCalendar
by changing the extension from "vcs" to "ics".

You can also export to HTML, e.g. for printing. You can adjust
the appearance of the HTML timetable by editing the style
sheet timetable-html.css.



OTHER FUNCTIONALITY
===============================================================

By double-clicking on events they become inactivated and
will not be exported. Inactivated events are shown in grey.

You can start the program in text mode by using the
parameters "today" and "tomorrow". The timetable for today
and tomorrow will then be printed.

From March 1 you can choose courses for the autumn, and
from October 1 you can choose courses for the spring. (If
they are available.) This only affects Daisy courses -- you
can always choose any TimeEdit course that is available in
the system.

