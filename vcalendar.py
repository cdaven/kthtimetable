# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import error
import timetable

def isUTF8(string):
    "Klarar åtminstone åäö men inte hela UTF-8!"
    if "Ã" in string: return True
    return False

def splitLine(line):
    "Delar raden vid första kolonet. Följande tecken kan innehålla kolon."    
    pos = line.find(":")
    return (line[:pos], line[pos+1:].strip())

# -----------------------------------------------------------
class Reader:
    "Läser en starkt begränsad form av vCalendar-data"

    def verifyFormat(self, data):
        if data[0].startswith("BEGIN:VCALENDAR") and \
        data[-1].startswith("END:VCALENDAR"):
            return True
        else:
            return False

    def read(self, input):
        "Läser vCalendar-data antingen från en lista eller från en fil"

        if not isinstance(input, list):
            try:
                input = file(input).readlines()
            except IOError:
                raise error.ReadError(_("Kan inte lasa fran fil") + " " + input, input)

        if not self.verifyFormat(input):
            raise error.DataError(_("Felaktig vCalendar-data"))

        events = []
        import encodings

        for line in input:
            (key, value) = splitLine(line)

            # får UTF-8-kodade värden från Daisy;
            # gör om dem till unicode-strängar
            if isUTF8(value):
                value = unicode(value, "utf8")

            if key == "BEGIN" and value == "VEVENT":
                id = date = begin = end = location = summary = ""

            elif key == "END" and value == "VEVENT":
                if id:
                    events.append({"id": id, "date": date, "begin": begin, "end": end,
                        "location": location, "summary": summary})
                    id = date = begin = end = location = summary = ""

            elif key == "UID":
                id = value

            elif key.startswith("DTSTART"):
                start = value.split("T")
                date = start[0]
                begin = start[1]

            elif key.startswith("DTEND"):
                end = value.split("T")[1]

            elif key == "SUMMARY":
                summary = value

            elif key == "LOCATION":
                location = value

        return events

# -----------------------------------------------------------
class Writer:
    "Skriver vCalendar-filer"

    def __init__(self, prodid = "-//cda//NONSGML Schema//SV"):
        self.prodid = prodid
    
    def write(self, events, filename):
        "Skriver valda händelser till vCalendar-fil"

        data = ["BEGIN:VCALENDAR\n", "VERSION:1.0\n", "PRODID:" + self.prodid + "\n"]
        for event in events:
            data.append("BEGIN:VEVENT")
            data.append("\nUID:" + str(event.getID()))
            
            # åtminstone Outlook och Palm Desktop utgår från att importerad data
            # är angiven i UTC utan hänsyn till sommartid
            begin = event.begin - 3600 # justerar tidszon
            end = event.end - 3600

            if event.date.isDaylightSavingTime():
                begin -= 3600 # justerar ev. sommartid
                end -= 3600

            data.append("\nDTSTART:" + str(event.date) + "T" + str(begin) + "Z")
            data.append("\nDTEND:" + str(event.date) + "T" + str(end) + "Z")
            data.append("\nSUMMARY:" + event.getDescriptionWithoutLocation().encode("latin_1"))
            data.append("\nLOCATION:" + event.location.encode("latin_1"))
            data.append("\nCATEGORIES:KTHTimeTable")
            data.append("\nEND:VEVENT\n")

        data.append("END:VCALENDAR")
        
        try:
            file(filename, "w+").writelines(data)
        except IOError:
            raise error.WriteError(_("Kan inte skriva till fil"), filename)

