# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import internet
import urllib
import re
import timetable
import error
import settings

# -----------------------------------------------------------
class Conduit:
    "Loggar in och h�mtar genererat schema fr�n Daisy"
    
    def __init__(self, callback = None):
        self.callback = callback
        self.urlopener = internet.CookieURLopener()
        self.loggedin = False

    def __del__(self):
        if self.loggedin:
            self.logout()
            
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
            raise error.ReadError(_("Kunde inte lasa fran") + " " + _("schemaservern"))

        start = generated.find("/servlet/schema.ics")
        end = generated.find("\"", start)

        if start == -1 or end == -1:
            raise error.DataError

        url = self.urlopener.open("http://daisy.it.kth.se" + generated[start:end])
        if self.callback: self.callback()

        data = url.readlines()

        if settings.in_debug_mode:
            file("dbg-daisydata", "w+").writelines(data)
            print "skrev h�mtad data till fil"

        return data

    def login(self, username, password):
        pass

    def login_X(self, username, password):
        postdata = urllib.urlencode({"anvnamn": username, "losenord": password})
        
        output = self.urlopener.open("https://daisy.it.kth.se/servlet/DaisyStudentInloggning",
            postdata).read()

        if output.find("Felaktig inloggning") != -1:
            self.loggedin = False
            raise error.LoginError

        self.loggedin = True

    def logout(self):
        pass

    def logout_X(self):
        if self.loggedin:
            try:
                self.urlopener.open("https://daisy.it.kth.se/servlet/LoggaUt")
            except IOError:
                pass
            
    def getTimeTableData_X(self, courseids):
        postdata = urllib.urlencode({"table": "true"})

        for id in courseids:
            postdata += "&" + urllib.urlencode({"momentid": id})

        generated = self.urlopener.open("https://daisy.it.kth.se/servlet/schema.SchemaGenerator",
            postdata).read()

        start = generated.find("schema.pdf.Pdf", 2000)
        end = generated.find("\"", start)

        if start == -1 or end == -1:
            raise error.DataError

        if self.callback: self.callback()

        return self.urlopener.open("https://daisy.it.kth.se/servlet/schema.ics?" +
            generated[start+14:end]).readlines()

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
