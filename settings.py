# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

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
        V�nsterledet �r "case-sensitive" och kan inneh�lla :.
        Avgr�nsare mellan f�lt och v�rde m�ste allts� vara =.
    """

    import re

    OPTCRE = re.compile(
        r'(?P<option>[^=\s][^=]*)'
        r'\s*(?P<vi>[=])\s*'



        r'(?P<value>.*)$'
        )

    # ist�llet f�r att f�lten ska skrivas med gemener
    # skrivs de helt enkelt som de �r (i str�ngrepresentation)
    # (pekar om funktionen optionxform(option) till str(option))
    optionxform = str

# -----------------------------------------------------------
timetablefile = os.path.join(os.getcwd(), "timetable")

# -----------------------------------------------------------
#  INST�LLNINGAR
# -----------------------------------------------------------
import calendar

daybegin = calendar.Time("080000")
dayend = calendar.Time("200000")
lastweekday = calendar.FRI

eventtype_examination = ["Salsskrivning", "Kontrollskrivning", "Dugga", "Tentamen"]
event_export_category = "KTHTimeTable"

in_debug_mode = False
