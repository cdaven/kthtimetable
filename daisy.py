# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import internet
import urllib
import re
import timetable
import error
import settings

# -----------------------------------------------------------
class Conduit:
    "Loggar in och hämtar genererat schema från Daisy"
    
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
            print "skrev hämtad data till fil"

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
        Tolkar Daisy-systemets 'summary'-fält i vCalendar-exporterade
        scheman och extraherar data.

        Denna "parsning" bygger på att summary-fältet i Daisys
        genererade scheman alltid har samma struktur -- förändras
        den måste denna kod förändras.

        ex. "Föreläsning 8 Sal E - Digital elektro"
    """
    
    def __init__(self):
        self.rxtype = re.compile("^(.*?)(  | [0-9A-ZÅÄÖ])")
        self.rxseries = re.compile("^[A-ZÅÄÖ][a-zåäö ]+ (\d{1,2}) ")
        self.rxgroup = re.compile("grp (\d+) ")
        self.rxcourse = re.compile("- (.+)$")

    # -----
    #  Observerade händelsetyper i Daisy:
    #  (anställda kan lägga in fritext som typ)

    #  Föreläsning

    #  Övning
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
    #  SI-möte
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
        "Hittar händelsens typ (ex. Föreläsning)"
        
        type = ""
        rx = self.rxtype.search(text)
        if rx:
            type = rx.group(1)
            
        return type

    def extractSeriesNo(self, text):
        "Hittar händelsens löpnummer (ex. (Lektion) 3)"
        
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
        # kan innehålla alla tecken, ex. "SPÖK , kvällskurs" och "*:59/2I1042/2I4033"
        rx = self.rxcourse.search(text)
        if rx:
            code = rx.group(1)
            
        return code
