# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import error
from i18n import *

def isUTF8(string):
    "Klarar �tminstone ��� men inte hela UTF-8!"
    if "�" in string: return True
    return False

def splitLine(line):
    "Delar raden vid f�rsta kolonet. F�ljande tecken kan inneh�lla kolon."    
    pos = line.find(":")
    return (line[:pos], line[pos+1:].strip())

# -----------------------------------------------------------
class Reader:
    "L�ser en starkt begr�nsad form av vCalendar-data"

    def verifyFormat(self, data):
        if data[0].startswith("BEGIN:VCALENDAR") and \
        data[-1].startswith("END:VCALENDAR"):
            return True
        else:
            return False

    def read(self, input):
        "L�ser vCalendar-data antingen fr�n en lista eller fr�n en fil"

        if not isinstance(input, list):
            try:
                input = file(input).readlines()
            except IOError:
                raise error.ReadError("Could not read from " + str(input))

        if not self.verifyFormat(input):
            raise error.DataError("Bad vCalendar data")

        events = []
        summarycontinues = False
        import encodings

        for line in input:
            # f�r UTF8-kodade v�rden fr�n Daisy
            # och Latin1-ditto fr�n TimeEdit;
            # g�r om dem till unicode-str�ngar
            if isUTF8(line):
                line = unicode(line, "utf8")
            else:
                line = unicode(line, "latin_1")

            (key, value) = splitLine(line)

            if key == "BEGIN" and value == "VEVENT":
                id = date = begin = end = location = summary = ""

            elif key == "END" and value == "VEVENT":
                if id:
                    events.append({"id": id, "date": date, "begin": begin, "end": end,
                        "location": location, "summary": summary})
                    id = date = begin = end = location = summary = ""

            elif key.startswith("UID"):
                id = value

            elif key.startswith("DTSTART"):
                start = value.split("T")
                date = start[0]
                begin = start[1]

            elif key.startswith("DTEND"):
                end = value.split("T")[1]

            elif key.startswith("SUMMARY"):
                summary = value
                if value[-1] == "=":
                    # l�nga rader kan brytas med '='
                    summarycontinues = True

            elif key.startswith("LOCATION"):
                location = value

            elif summarycontinues:
                summary = summary[:-1] + line.strip()
                summarycontinues = False

        return events

# -----------------------------------------------------------
class Writer:
    "Skriver vCalendar-filer"

    def __init__(self, encoding = "latin_1"):
        self.encoding = encoding
    
    def write(self, events, UTC = True):
        "Skriver valda h�ndelser till vCalendar-fil"

        import settings

        data = ["BEGIN:VCALENDAR\n", "VERSION:1.0\n", "PRODID:-//cda//NONSGML KTHTT//EN\n"]
        for event in events:
            data.append("BEGIN:VEVENT")
            data.append("\nUID:" + str(event.getID()))

            begin = event.begin
            end = event.end

            if UTC:
                # de flesta program utg�r fr�n att tiden
                # �r angiven i UTC utan h�nsyn till sommartid
                begin -= 3600 # justerar tidszon
                end -= 3600

                if event.date.isDaylightSavingTime():
                    begin -= 3600 # justerar ev. sommartid
                    end -= 3600

            data.append("\nDTSTART:" + str(event.date) + "T" + str(begin) + "Z")
            data.append("\nDTEND:" + str(event.date) + "T" + str(end) + "Z")
            data.append("\nSUMMARY:" + event.getDescriptionWithoutLocation().encode(self.encoding))
            data.append("\nLOCATION:" + event.location.encode(self.encoding))
            data.append("\nCATEGORIES:" + settings.event_export_category)
            data.append("\nEND:VEVENT\n")

        data.append("END:VCALENDAR")
        return data

