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
            
    def getvCalendarData(self, username, password, courseids):
        try:
            self.login(username, password)
            if self.callback: self.callback()
            data = self.getTimeTableData(courseids)
        except IOError:
            raise error.ReadError("Kunde inte läsa från Daisy-servern")

        if self.callback: self.callback()
        self.logout()

        if settings.in_debug_mode:
            file("dbg-daisydata", "w+").writelines(data)
            print "skrev hämtad data till fil"

        return data

    def login(self, username, password):
        postdata = urllib.urlencode({"anvnamn": username, "losenord": password})
        
        output = self.urlopener.open("https://daisy.it.kth.se/servlet/DaisyStudentInloggning",
            postdata).read()

        if output.find("Felaktig inloggning") != -1:
            self.loggedin = False
            raise error.LoginError

        self.loggedin = True

    def logout(self):
        if self.loggedin:
            try:
                self.urlopener.open("https://daisy.it.kth.se/servlet/LoggaUt")
            except IOError:
                pass
            
#    def verifyDocument(self, document):
#        if len(document) < 10000:
#            return False
#        elif document.find("<title>Student -") == -1:
#            return False
#        else:
#            return True

    def getTimeTableData(self, courseids):
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
    
    # -----
    #  Observerade händelsetyper i Daisy:

    #  Föreläsning

    #  Övning
    #  Lektion
    #  Seminarium
    #  Laboration
    
    #  Kontrollskrivning
    #  Dugga
    #  Salsskrivning

    #  Redovisning
    #  Information
    #  Introduktion
    #  Handledning
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
        rx = re.search("^([A-ZÅÄÖ][a-zåäö ]+) [0-9A-ZÅÄÖ]", text)
        if rx:
            type = rx.group(1)
            
        return type

    def extractSeriesNo(self, text):
        "Hittar händelsens löpnummer (ex. (Lektion) 3)"
        
        number = 0
        rx = re.search("^[A-ZÅÄÖ][a-zåäö ]+ (\d{1,2}) ", text)
        if rx:
            number = int(rx.group(1))
                
        return number

    def extractGroup(self, text):
        "Hittar eventuellt gruppnummer"
        
        group = 0
        rx = re.search("grp (\d+) ", text)
        if rx:
            group = int(rx.group(1))
        
        return group
        
    def extractCourse(self, text):    
        "Hittar kursbeteckningen"
        
        code = ""
        # kan innehålla alla tecken, ex. "SPÖK , kvällskurs" och "*:59/2I1042/2I4033"
        rx = re.search("- (.+)$", text)
        if rx:
            code = rx.group(1)
            
        return code
