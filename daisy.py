# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import urllib
import re
import timetable
import calendar
import error
import settings
import htmlentitydefs
from i18n import *

# -----------------------------------------------------------
class Conduit:
    "Loggar in och h�mtar genererat schema fr�n Daisy"
    
    def __init__(self, callback = None):
        self.callback = callback

    def getvCalendarData(self, courseids):
        getdata = "?generator=true"

        for id in courseids:
            getdata += "&momentid=" + str(id)

        try:
            url = urllib.urlopen("http://daisy.it.kth.se/servlet/anstalld.schema.BoardSchema" + getdata)
            if self.callback: self.callback()
            generated = url.read()
            if self.callback: self.callback()
        except IOError:
            raise error.ReadError(U_("Could not read from") + " " + U_("the timetable server"))

        start = generated.find("/servlet/schema.ics")
        end = generated.find("\"", start)

        if start == -1 or end == -1:
            raise error.DataError

        url = urllib.urlopen("http://daisy.it.kth.se" + generated[start:end])
        if self.callback: self.callback()

        return url.readlines()

    def getCourses(self, callback = None):
        """
            H�mtar alla valbara kurser p� IT-universitetet f�r aktuell termin.
            Callback anv�nds f�r att visa f�rloppet f�r anv�ndaren
        """

        vt = "1"
        ht = "2"
        today = calendar.Date()
        year = today.getYear()
        courses = []

        # efter oktober h�mtas aktuell h�sttermin plus kommande v�rtermin
        if today.getMonth() > 9:
            courses = self.getCoursesForPeriod(str(year) + ht, callback)
            courses += self.getCoursesForPeriod(str(year + 1) + vt, callback)
        # f�re mars h�mtas f�reg�ende �rs h�sttermin plus aktuell v�rtermin
        elif today.getMonth() < 3:
            courses = self.getCoursesForPeriod(str(year - 1) + ht, callback)
            courses += self.getCoursesForPeriod(str(year) + vt, callback)
        # mellan mars och oktober h�mtas v�rtermin och h�sttermin f�r samma �r
        else:
            courses = self.getCoursesForPeriod(str(year) + vt, callback)
            courses += self.getCoursesForPeriod(str(year) + ht, callback)

        return courses

    def getCoursesForPeriod(self, period, callback):
        try:
            url = urllib.urlopen("http://www.it.kth.se/schema.html?termin=" + period +
                "&program=0&institution=0&Visa=Visa")
        except IOError:
            raise error.ReadError(U_("Could not read from") + " www.it.kth.se/schema.html", "www.it.kth.se/schema.html")

        if callback: callback()
        input = url.read()

        if len(input) == 0:
            raise error.DataError(U_("Received no data from") + " " + U_("the timetable server"))

        all = re.findall("value=\"(\d{3,})\"[^a-z���A-Z���0-9]*(.*?) \((.*?)\)", self.descape(input))
        courses = []
        for a in all:
            courses.append(timetable.Course(code=a[2].strip(), name=a[1].strip(), id=a[0], term=period))

        if callback: callback()
        return courses

    def descape(self, text):
        "�vers�tter fr�n html till specialtecken"

        text = text.replace("&#38;", "&")
        return re.sub("&(\w+?);", self.descape_entity, text)

    def descape_entity(self, rx):
        "Anv�nds endast av descape() via re.sub()"

        if rx.group(1) in htmlentitydefs.entitydefs:
            return htmlentitydefs.entitydefs[rx.group(1)]
        else:
            return rx.group(0)


# -----------------------------------------------------------
class SummaryParser:
    """
        Tolkar Daisy-systemets 'summary'-f�lt i vCalendar-exporterade
        scheman och extraherar data.

        Denna "parsning" bygger p� att summary-f�ltet i Daisys
        genererade scheman alltid har samma struktur -- f�r�ndras
        den m�ste denna kod f�r�ndras.

        ex. "F�rel�sning 8 Sal E - Digital elektro"
    """
    
    def __init__(self):
        self.rxtype = re.compile("^(.*?)(  | [0-9A-Z���])")
        self.rxseries = re.compile("^[A-Z���][a-z��� ]+ (\d{1,2}) ")
        self.rxgroup = re.compile("grp (\d+) ")
        self.rxcourse = re.compile("- (.+)$")

    # -----
    #  Observerade h�ndelsetyper i Daisy:
    #  (anst�llda kan l�gga in fritext som typ)

    #  F�rel�sning

    #  �vning
    #  Lektion
    #  Seminarium
    #  Laboration
    #  Designseminarium
    
    #  Kontrollskrivning
    #  Dugga
    #  Salsskrivning

    #  Redovisning
    #  Information
    #  Introduktion
    #  Handledning
    #  SI-m�te
    # -----

    def parse(self, summary):
        data = {}
        data["type"] = self.extractType(summary)
        data["seriesno"] = self.extractSeriesNo(summary)
        data["group"] = self.extractGroup(summary)
        data["course"] = self.extractCourse(summary)
        data["location"] = ""
        return data
    
    def extractType(self, text):
        "Hittar h�ndelsens typ (ex. F�rel�sning)"
        
        type = ""
        rx = self.rxtype.search(text)
        if rx:
            type = rx.group(1)
            
        return type

    def extractSeriesNo(self, text):
        "Hittar h�ndelsens l�pnummer (ex. (Lektion) 3)"
        
        number = 0
        rx = self.rxseries.search(text)
        if rx:
            number = int(rx.group(1))
                
        return number

    def extractGroup(self, text):
        "Hittar eventuellt gruppnummer"
        
        group = ""
        rx = self.rxgroup.search(text)
        if rx:
            group = rx.group(1)
        
        return group
        
    def extractCourse(self, text):    
        "Hittar kursbeteckningen"
        
        code = ""
        # kan inneh�lla alla tecken, ex. "SP�K , kv�llskurs" och "*:59/2I1042/2I4033"
        rx = self.rxcourse.search(text)
        if rx:
            code = rx.group(1)
        
        return code
