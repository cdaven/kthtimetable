#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

# Hela programvarans kod faller under "The GNU General Public License"
# som finns längst ned i detta dokument i en kortfattad variant. För
# hela licenstexten, se: <http://www.gnu.org/copyleft/gpl.html>

import sys
import os, os.path
import settings
from i18n import *

settings.load()

# Raderar alla tmpXXXXXX-filer som skapats av PyInformationalMessagesFrame
files = os.listdir(os.getcwd())
for file in files:
    if file.startswith("tmp") and os.path.isfile(os.path.join(os.getcwd(), file)):
        os.remove(os.path.join(os.getcwd(), file))

if len(sys.argv) > 1:
    import timetable
    import calendar
    if sys.argv[1] == "today":
        events = timetable.timetable.getEventsForDate(calendar.Date())
    elif sys.argv[1] == "tomorrow":
        events = timetable.timetable.getEventsForDate(calendar.Date() + 1)
    else:
        print U_("Unknown command")
        sys.exit(1)
        
    events = timetable.EventSorter().sort(events)
    for event in events:
        if event.active: print event.getNiceString()
else:
    try:
        import wx
        import wx.lib.infoframe
    except:
        print U_("Could not start wxPython.\nPlease make sure your installed version of wxPython is compatible with your Python version.")
        sys.exit(1)    
    
    import gui
    
    class Application(wx.App):
        def OnInit(self):
            # skickar felinfo till ett fönster
            sys.stderr = wx.lib.infoframe.PyInformationalMessagesFrame()

            main = gui.MainFrame()
            main.Show(1)
            self.SetTopWindow(main)
            return True
        
    app = Application(0)
    app.MainLoop()

settings.save()

# -----------------------------------------------------------
# The GNU General Public License is a Free Software license. Like any Free
# Software license, it grants to you the four following freedoms:
# 
# 0. The freedom to run the program for any purpose.
# 1. The freedom to study how the program works and adapt it to your needs.
# 2. The freedom to redistribute copies so you can help your neighbor.
# 3. The freedom to improve the program and release your improvements to the
#    public, so that the whole community benefits.
# 
# You may exercise the freedoms specified here provided that you comply with the
# express conditions of this license. The principal conditions are:
# 
# You must conspicuously and appropriately publish on each copy distributed an
# appropriate copyright notice and disclaimer of warranty and keep intact all the
# notices that refer to this License and to the absence of any warranty; and give
# any other recipients of the Program a copy of the GNU General Public License
# along with the Program. Any translation of the GNU General Public License must
# be accompanied by the GNU General Public License.
# 
# If you modify your copy or copies of the program or any portion of it, or
# develop a program based upon it, you may distribute the resulting work provided
# you do so under the GNU General Public License. Any translation of the GNU
# General Public License must be accompanied by the GNU General Public License.
# 
# If you copy or distribute the program, you must accompany it with the complete
# corresponding machine-readable source code or with a written offer, valid for
# at least three years, to furnish the complete corresponding machine-readable
# source code.
# 
# Any of these conditions can be waived if you get permission from the copyright
# holder.
# 
# Your fair use and other rights are in no way affected by the above.
# -----------------------------------------------------------

