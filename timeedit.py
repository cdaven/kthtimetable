# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import urllib
import calendar
import re
import error
import settings
import timetable
from i18n import *

# -----------------------------------------------------------
class Conduit:
    "Hämtar schema från KTH:s centrala schemagenerator"

    def __init__(self, callback = None):
        self.urlopener = urllib.FancyURLopener()
        self.callback = callback
        
    def getTimeTableURL(self, coursecodes):
        url = "http://schema.sys.kth.se/4DACTION/iCal_GetReservations/"
        url += self.getFromYearAndWeek() + "/"
        url += self.getToYearAndWeek()

        for code in coursecodes:
            url += "/" + code
            
        return url + ".vcs"

    def getvCalendarData(self, coursecodes):
        try:
            url = self.urlopener.open(self.getTimeTableURL(coursecodes))
            if self.callback: self.callback()
            return url.readlines()
        except IOError:
            raise error.ReadError(U_("Could not read from") + " " + U_("the timetable server"))
    
    def getFromYearAndWeek(self):
        date = calendar.Date() - 14
        week = str(date.getWeek())
        if len(week) == 1: week = "0" + week
        return str(date.getYear() - 2000) + week
    
    def getToYearAndWeek(self):
        today = calendar.Date()
        year = today.getYear() - 2000

        if today.getMonth() > 9:
            year = str(year + 1)
            week = "35" # sista tänkbara omtentavecka i augusti (?)
        elif today.getMonth() < 3:
            year = str(year)
            week = "35"
        else:
            year = str(year)
            week = "51"

        return year + week

    def getCourseInfo(self, code):
        url = "http://schema.sys.kth.se/4DACTION/WebShowSearch/1/1-3"
        getdata = urllib.urlencode({"wv_search": code, "wv_bSearch": "Sök", "wv_type": 4})

        try:
            data = self.urlopener.open(url, getdata).read()
        except IOError:
            raise error.ReadError(U_("Could not read from") + " " + U_("the timetable server"))

        rxcode = re.escape(code)
        rx = re.search("<TD>(" + rxcode + ")</TD>.*<TD>(\w.*?)</TD>", data, re.DOTALL|re.IGNORECASE)
        if not rx:
            raise ValueError(U_("The course ") + code + " " + U_("does not exist"))
        
        return timetable.Course(rx.group(1), rx.group(2))

# -----------------------------------------------------------
class SummaryParser:

    def __init__(self):
        self.types = {"DL": u"Datalaboration", "Frl": u"Föreläsning", "FÖ": u"Fältövning",
            "Lab": u"Laboration", "Le": u"Lektion", "Proj": u"Projekt", "RS": u"Räknestuga",
            "Sem": u"Seminarium", "Stu": u"Studiebesök", "WS": u"Workshop", "KS": u"Kontrollskrivning",
            "Ovn": u"Övning", "TEN": u"Tentamen"}
        self.lowercase_letters = u"abcdefghijklmnopqrstuvwxyzåäö"
        self.numbers = "1234567890"

        self.rxcourse = re.compile("(\d\D\d{4})(\.(\D))?")
        self.rxtype = re.compile("([a-zåäöA-ZÅÄÖ]{2,4})")
        self.rxlocation = re.compile("([A-Z]{1,2}\d+)")

    def parse(self, summary):
        data = {}
        (data["course"], data["group"]) = self.extractCourseAndGroup(summary)
        data["type"] = self.extractType(summary)
        data["location"] = self.extractLocation(summary)
        data["seriesno"] = 0
        return data
    
    def extractLocation(self, text):
        words = text.split(",")
        words.reverse() # söker från slutet
        locations = []

        for word in words:
            rx = self.rxlocation.match(word.strip())
            if rx:
                locations.append(rx.group(1) + ",")
            else:
                # Så fort orden inte längre är lokaler
                # kommer det inga fler
                break

        locationstring = ""
        locations.reverse()
        for location in locations:
            locationstring += location

        return locationstring[:-1]
            
    def extractCourseAndGroup(self, text):
        words = text.split(",")
        coursestring = ""
        group = ""

        for word in words:
            rx = self.rxcourse.match(word.strip())
            if rx:
                coursestring += rx.group(1) + ","
                if rx.group(3): group = rx.group(3)
            else:
                # Så fort orden inte längre är kurser
                # kommer det inga fler
                break

        return (coursestring[:-1], group)

    def extractType(self, text):
        typecode = ""
        rx = self.rxtype.search(text)
        if rx:
            typecode = rx.group(1)

        try:
            type = self.types[typecode]
        except KeyError:
            type = typecode

        return type
        
