# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2005

import error
import timetable
from i18n import *

# DAISYKTH40818|20050103|080000|100000|Projects and Powergames F11|Sal A

class Reader:
    "Läser ett specialdesignat kalenderformat"

    def read(self, input):
        pass

class Writer:
    def write(self, events):
        "Skriver inte till fil utan returnerar en sträng"

        string = ""

        for event in events:
            string += str(event.getID()) + "|"
            string += str(event.date) + "|"
            string += str(event.begin) + "|"
            string += str(event.end) + "|"
            string += event.getDescriptionWithoutLocation().encode("latin_1") + "|"
            string += event.location.encode("latin_1") + "\n"

        return string
