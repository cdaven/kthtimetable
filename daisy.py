# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import urllib
import re
import timetable
import calendar
import error
import settings
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

        data = url.readlines()

        if settings.in_debug_mode:
            file("dbg-daisydata", "w+").writelines(data)
            print "skrev h�mtad data till fil"

        return data

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
        
        group = 0
        rx = self.rxgroup.search(text)
        if rx:
            group = int(rx.group(1))
        
        return group
        
    def extractCourse(self, text):    
        "Hittar kursbeteckningen"
        
        code = ""
        # kan inneh�lla alla tecken, ex. "SP�K , kv�llskurs" och "*:59/2I1042/2I4033"
        rx = self.rxcourse.search(text)
        if rx:
            code = rx.group(1)
            
        return code

# -----------------------------------------------------------
def getITUCourses(input = None, callback = None):
    """
        H�mtar alla valbara kurser p� IT-universitetet f�r aktuell termin.
        Callback anv�nds f�r att visa f�rloppet f�r anv�ndaren
    """
    
    if not isinstance(input, str):
        period = getYearTerm()
        try:
            url = urllib.urlopen("http://www.it.kth.se/schema.html?termin=" + period +
                "&program=0&institution=0&Visa=Visa")
        except IOError:
            raise error.ReadError(U_("Could not read from") + " www.it.kth.se/schema.html", "www.it.kth.se/schema.html")

        if callback: callback()
        input = url.read()

    if callback: callback()

    if len(input) == 0:
        raise error.DataError(U_("Received no data from") + " " + U_("the timetable server"))

    import timetable
    all = re.findall("value=\"(\d{3,})\"[^a-z���A-Z���0-9]*(.*?) \((.*?)\)", descape(input))
    courses = []
    for a in all:
        courses.append(timetable.Course(a[2].strip(), a[1].strip(), int(a[0])))

    return courses

def getYearTerm():
    week = calendar.Date().getWeek()
    year = calendar.Date().getYear()

    if week >= 52: year += 1

    if week > 30 and week < 52: term = "2" # h�sttermin
    else: term = "1" # v�rtermin

    return str(year) + term

def descape(text):
    "�vers�tter fr�n html till specialtecken"

    text = text.replace("&#38;", "&")
    return re.sub("&(\w+?);", descape_entity, text)

def descape_entity(rx):
    "Anv�nds endast av descape() via re.sub()"

    import htmlentitydefs
    
    if rx.group(1) in htmlentitydefs.entitydefs:
        return htmlentitydefs.entitydefs[rx.group(1)]
    else:
        return rx.group(0)
