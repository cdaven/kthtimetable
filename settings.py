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
lastweekday = 4
eventtype_examination = ["Salsskrivning", "Kontrollskrivning", "Dugga", "Tentamen"]
event_export_category = "KTHTimeTable"
language = "en"
preferred_system = "Daisy"
publish_userid = ""
publish = False

# -----------------------------------------------------------
def _setDefaultCalendarValues():
    global daybegin, dayend, lastweekday
    import calendar
    daybegin = calendar.Time("080000")
    dayend = calendar.Time("200000")
    lastweekday = calendar.FRI


def load():
    global __filename, language

    setLanguage(language)
    loadFromFile(__filename)


def loadFromFile(filename):
    global daybegin, dayend, lastweekday, event_export_category, language
    global preferred_system, publish_userid, publish

    config = configfileparser.ConfigParserX()

    try:
        config.readfp(file(__filename))
    except IOError:
        sys.stderr.write("Settings missing, using default values.\n")
        _setDefaultCalendarValues()
        return

    try:
        language = config.get("main", "language")
        setLanguage(language)
    except (error.DataError, IOError):
        sys.stderr.write("Settings missing or invalid, using default values.\n")

    try:
        publish = config.getboolean("main", "publish")
        publish_userid = config.get("main", "publish_userid")
    except error.DataError:
        sys.stderr.write("Settings missing or invalid, using default values.\n")

    import calendar

    try:
        daybegin = calendar.Time(config.get("main", "daybegin"))
        dayend = calendar.Time(config.get("main", "dayend"))
        lastweekday = int(config.get("main", "lastweekday"))
    except (error.DataError, ValueError):
        _setDefaultCalendarValues()
        sys.stderr.write("Settings missing or invalid, using default values.\n")

    try:
        preferred_system = config.get("main", "preferred_system")
        event_export_category = config.get("main", "event_export_category")
    except (error.DataError, IOError):
        sys.stderr.write("Settings missing or invalid, using default values.\n")


def save():
    global daybegin, dayend, lastweekday, event_export_category, language
    global preferred_system, __filename, publish_userid, publish

    config = configfileparser.ConfigParserX()

    config.add_section("main")
    config.set("main", "daybegin", str(daybegin))
    config.set("main", "dayend", str(dayend))
    config.set("main", "lastweekday", str(lastweekday))
    config.set("main", "event_export_category", event_export_category)
    config.set("main", "language", language)
    config.set("main", "preferred_system", preferred_system)
    config.set("main", "publish_userid", publish_userid)
    config.set("main", "publish", str(publish))

    try:
        config.write(file(__filename, "w+"))
    except IOError:
        raise error.WriteError(U_("Could not write to"), __filename)
