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
import ConfigParser
class ConfigParser(ConfigParser.SafeConfigParser):
    """
        Subklass till SafeConfigParser.
        Vänsterledet är "case-sensitive" och kan innehålla :.
        Avgränsare mellan fält och värde måste alltså vara =.
    """

    import re

    OPTCRE = re.compile(
        r'(?P<option>[^=\s][^=]*)'
        r'\s*(?P<vi>[=])\s*'



        r'(?P<value>.*)$'
        )

    # istället för att fälten ska skrivas med gemener
    # skrivs de helt enkelt som de är (i strängrepresentation)
    # (pekar om funktionen optionxform(option) till str(option))
    optionxform = str

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
