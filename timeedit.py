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
        url = "http://schema.sys.kth.se/4DACTION/iCalGetEntries/"
        url += self.getFromYearAndWeek() + "/"
        url += self.getToYearAndWeek()

        for code in coursecodes:
            url += "/" + code
            
        url += ".ics"
        return url

    def getvCalendarData(self, coursecodes):
        try:
            url = self.urlopener.open(self.getTimeTableURL(coursecodes))
            if self.callback: self.callback()
            data = url.readlines()
            if settings.in_debug_mode:
                file("dbg-timeeditdata", "w+").writelines(data)
                print "skrev hämtad data till fil"
            return data
        except IOError:
            raise error.ReadError(U_("Could not read from") + " " + U_("the timetable server"))
    
    def getFromYearAndWeek(self):
        week = str((calendar.Date() - 14).getWeek())
        if len(week) == 1: week = "0" + week
        return str(calendar.Date().getYear() - 2000) + week
    
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
        rx = re.search("<TD>" + rxcode + "</TD>.*<TD>(\w.*?)</TD>", data, re.DOTALL|re.IGNORECASE)
        if not rx:
            raise ValueError(U_("The course") + " " + code + " " + U_("does not exist"))
        
        return timetable.Course(code.upper(), rx.group(1))

# -----------------------------------------------------------
class SummaryParser:

    def __init__(self):
        self.types = {"DL": u"Datalaboration", "F": u"Föreläsning", "FÖ": u"Fältövning",
            "L": u"Laboration", "Le": u"Lektion", "Proj": u"Projekt", "RS": u"Räknestuga",
            "Sem": u"Seminarium", "Stu": u"Studiebesök", "WS": u"Workshop",
            "Ö": u"Övning", "TEN": u"Tentamen"}
        self.lowercase_letters = u"abcdefghijklmnopqrstuvwxyzåäö"
        self.numbers = "1234567890"

        self.rxcourse = re.compile("([A-Z0-9:/*]+?)\.")
        self.rxtype = re.compile("\.([A-ZÅÄÖa-z]+)")

    def parse(self, summary):
        data = {}
        data["location"] = self.extractLocation(summary)
        data["course"] = self.extractCourse(summary)
        data["type"] = self.extractType(summary)
        data["seriesno"] = 0
        data["group"] = 0
        return data
    
    def extractLocation(self, text):
        words = text.split(" ")
        words.reverse()
        locations = []
        for word in words:
            if word[-1] in self.lowercase_letters or word[-1] in self.numbers:
                locations.append(word)
            elif word == "---" or word.endswith("..."):
                continue
            else:
                break

        locations.reverse()
        locationstring = ""
        for location in locations:
            if locationstring:
                locationstring += "," 
            locationstring += location
                
        return locationstring
            
    def extractCourse(self, text):
        course = "???"
        rx = self.rxcourse.search(text)
        if rx:
            course = rx.group(1)
        
        return course

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
        
