# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import os
import os.path
import sys
import calendar

# -----------------------------------------------------------
#  INST�LLNINGAR
# -----------------------------------------------------------
daybegin = calendar.Time("080000")
dayend = calendar.Time("200000")
lastweekday = calendar.FRI

eventtype_examination = ["Salsskrivning", "Kontrollskrivning", "Dugga", "Tentamen"]
event_export_category = "KTHTimeTable"

in_debug_mode = False

timetablefile = os.path.join(os.getcwd(), "timetable")

# -----------------------------------------------------------
def load():
    pass

def save():
    pass
