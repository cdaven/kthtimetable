# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import os
import os.path
import sys

# -----------------------------------------------------------
def load():
    pass

def save():
    pass

# -----------------------------------------------------------
timetablefile = os.path.join(os.getcwd(), "timetable")

# -----------------------------------------------------------
#  INSTÄLLNINGAR
# -----------------------------------------------------------
import calendar

daybegin = calendar.Time("080000")
dayend = calendar.Time("200000")
lastweekday = calendar.FRI

eventtype_examination = ["Salsskrivning", "Kontrollskrivning", "Dugga", "Tentamen"]
event_export_category = "KTHTimeTable"

in_debug_mode = False
