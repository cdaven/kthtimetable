# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import urllib
import calendar
import re
import error
import settings

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
            raise error.ReadError("Kunde inte läsa från schemaservern")
    
    def getFromYearAndWeek(self):
        week = str(calendar.Date().getWeek())
        if len(week) == 1: week = "0" + week
        return str(calendar.Date().getYear() - 2000) + week
    
    def getToYearAndWeek(self):
        year = calendar.Date().getYear() - 2000
        week = calendar.Date().getWeek()

        endweek = "30" # vårtermin
        if week > 30:
            # hösttermin, hämtar fram till årets sista vecka
            endweek = str(calendar.Date(str(calendar.Date().getYear()) + "1228").getWeek())

        if len(endweek) == 1: endweek = "0" + endweek
        return str(year) + endweek

    def getCourseInfo(self, code):
        url = "http://schema.sys.kth.se/4DACTION/WebShowSearch/1/1-3"
        getdata = urllib.urlencode({"wv_search": code, "wv_bSearch": "Sök", "wv_type": 3})

        try:
            data = self.urlopener.open(url, getdata).read()
        except IOError:
            raise error.ReadError("Kunde inte läsa från schema-servern")

        rxcode = re.escape(code)
        rx = re.search("<TD>" + rxcode + "</TD>.*<TD>(\w.*?)</TD>", data, re.DOTALL|re.IGNORECASE)
        if not rx:
            raise ValueError("kursen " + code + " existerar inte")
        
        import timetable
        return timetable.Course(code.upper(), rx.group(1))

# -----------------------------------------------------------
class SummaryParser:

    def __init__(self):
        self.types = {"F": "Föreläsning", "L": "Laboration", "Le": "Lektion",
            "Ö": "Övning", "Sem": "Seminarium", "WS": "Workshop",
            "TEN": "Tentamen"}
        self.lowercase_letters = "abcdefghijklmnopqrstuvwxyzåäö"
        self.numbers = "1234567890"

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
        rx = re.search("([A-Z0-9:/*]+?)\.", text)
        if rx:
            course = rx.group(1)
        
        return course

    def extractType(self, text):
        typecode = ""
        rx = re.search("\.([A-ZÅÄÖa-z]+)", text)
        if rx:
            typecode = rx.group(1)

        try:
            type = self.types[typecode]
        except KeyError:
            type = typecode

        return type
        
