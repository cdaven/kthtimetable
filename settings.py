# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import os
import os.path
import sys
import error
import i18n

i18n.setLanguage("en")

# -----------------------------------------------------------
timetablefile = os.path.join(os.getcwd(), "timetable")

# -----------------------------------------------------------
def load():
    global timetablefile
    import configfileparser
    config = configfileparser.ConfigParserX()
    try:
        config.readfp(file(timetablefile))
    except IOError:
        return

    try:
        i18n.setLanguage(config.get("settings", "language"))
    except error.DataError:
        return

def save():
    pass

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
