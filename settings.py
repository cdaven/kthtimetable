# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import os
import os.path
import sys
import error
import configfileparser
from i18n import *

__filename = "settings"
timetablefile = os.path.join(os.getcwd(), "timetable")
daybegin = None
dayend = None
lastweekday = 0
eventtype_examination = ["Salsskrivning", "Kontrollskrivning", "Dugga", "Tentamen"]
language = ""

in_debug_mode = False

# -----------------------------------------------------------
def setDefaults():
    global daybegin, dayend, lastweekday, event_export_category, language
    language = "en"
    setLanguage(language)
    import calendar
    daybegin = calendar.Time("080000")
    dayend = calendar.Time("200000")
    lastweekday = calendar.FRI
    event_export_category = "KTHTimeTable"

def load():
    global __filename, language
    
    try:
        loadFromFile(__filename)
    except (error.DataError, IOError):
        setDefaults()
        sys.stderr.write("The settings file is corrupt or missing. Using default settings.\n")

def loadFromFile(filename):
    global daybegin, dayend, lastweekday, event_export_category, language

    config = configfileparser.ConfigParserX()
    config.readfp(file(__filename))

    language = config.get("main", "language")
    setLanguage(language)

    import calendar
    daybegin = calendar.Time(config.get("main", "daybegin"))
    dayend = calendar.Time(config.get("main", "dayend"))
    lastweekday = int(config.get("main", "lastweekday"))
    event_export_category = config.get("main", "event_export_category")

def save():
    global daybegin, dayend, lastweekday, event_export_category, language, __filename

    config = configfileparser.ConfigParserX()

    config.add_section("main")
    config.set("main", "daybegin", str(daybegin))
    config.set("main", "dayend", str(dayend))
    config.set("main", "lastweekday", str(lastweekday))
    config.set("main", "event_export_category", event_export_category)
    config.set("main", "language", language)

    try:
        config.write(file(__filename, "w+"))
    except IOError:
        raise error.WriteError(U_("Could not write to"), __filename)
