#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import vcalendar
import calendar
import timetable
import error
import xunittest

# -----------------------------------------------------------
class ModuleTest(xunittest.TestCase):
    def testSplitLine(self):
        self.failUnlessEqual(vcalendar.splitLine("BEGIN:VEVENT"), ("BEGIN", "VEVENT"))
        self.failUnlessEqual(vcalendar.splitLine("DTSTAMP:20040224T160531"), ("DTSTAMP", "20040224T160531"))
        self.failUnlessEqual(vcalendar.splitLine("SUMMARY:Lektion 401 - *:59"), ("SUMMARY", "Lektion 401 - *:59"))

# -----------------------------------------------------------
class ReaderTest(xunittest.TestCase):
    def setUp(self):
        timetable.courselist.clear()
        timetable.courselist.addCourse("2B1345", "DigEl", 616, 2)
        timetable.courselist.addCourse("*:59", "DSV-mysko", 931)
        timetable.courselist.addCourse("DSV:L/9E1363", "Kommunikation", 429, 5)
        timetable.courselist.addCourse("5B1113", "Matte", 754)
        timetable.courselist.addCourse("9E1338", "TMS-franska", 338)
        timetable.courselist.addCourse("4D1225", "Projekt", 122, 5)
        timetable.courselist.addCourse("5B1506", "MatS", 156, 0)
    
    def testRead_Daisy(self):
        events = []
        events.append({"id": "DAISYKTH1000", "date": calendar.Date("20040301"), "begin": calendar.Time("110000"),
            "end": calendar.Time("130000"), "location": "Sal A", "summary": "Föreläsning 1 Sal A - 5B1113"})
        events.append({"id": "DAISYKTH1001", "date": calendar.Date("20040414"), "begin": calendar.Time("093000"),
            "end": calendar.Time("120000"), "location": "540", "summary": "Lektion 3 grp 2 540 - 2B1345"})
        events.append({"id": "DAISYKTH1002", "date": calendar.Date("20040414"), "begin": calendar.Time("153000"),
            "end": calendar.Time("180000"), "location": "Aulan", "summary": "Introduktion Aulan - DSV:L/9E1363"})
        events.append({"id": "DAISYKTH1003", "date": calendar.Date("20040416"), "begin": calendar.Time("100000"),
            "end": calendar.Time("120000"), "location": "Aulan", "summary": "Föreläsning 1 Aulan - DSV:L/9E1363"})

        data = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//DSV SU-KTH//NONSGML Daisy//SV", "BEGIN:VEVENT",
            "UID:DAISYKTH1000", "LAST-MODIFIED:20040530T115609", "DTSTART:20040301T110000", "DTEND:20040301T130000",
            "SUMMARY:Föreläsning 1 Sal A - 5B1113", "LOCATION:Sal A", "END:VEVENT", "BEGIN:VEVENT",
            "UID:DAISYKTH1001", "LAST-MODIFIED:20040530T115609", "DTSTART:20040414T093000", "DTEND:20040414T120000",
            "SUMMARY:Lektion 3 grp 2 540 - 2B1345", "LOCATION:540", "END:VEVENT", "BEGIN:VEVENT", "UID:DAISYKTH1002",
            "LAST-MODIFIED:20040530T115609", "DTSTART:20040414T153000", "DTEND:20040414T180000",
            "SUMMARY:Introduktion Aulan - DSV:L/9E1363", "LOCATION:Aulan", "END:VEVENT", "BEGIN:VEVENT", 
            "UID:DAISYKTH1003", "LAST-MODIFIED:20040530T115609", "DTSTART:20040416T100000", "DTEND:20040416T120000",
            "SUMMARY:Föreläsning 1 Aulan - DSV:L/9E1363", "LOCATION:Aulan", "END:VEVENT", "END:VCALENDAR"]

        self.failUnlessListsEqual(vcalendar.Reader().read(data), events)
        self.failUnlessRaises(error.ReadError, vcalendar.Reader().read, "eörjlkhqytbn")
        self.failUnlessRaises(error.DataError, vcalendar.Reader().read, __file__)

    def testRead_TimeEdit(self):
        events = []
        events.append({"id": "20040809T103009-26770@timeedit.evolvera.se", "date": calendar.Date("20041129"),
            "begin": calendar.Time("170000"), "end": calendar.Time("210000"), "location": "", "summary": "X3X X4X 9E1338.Le E34 ---"})
        events.append({"id": "20040809T103009-195910@timeedit.evolvera.se", "date": calendar.Date("20040923"),
            "begin": calendar.Time("130000"), "end": calendar.Time("150000"), "location": "", "summary": "4D1225.Sem X3X"})
        events.append({"id": "20040809T160814-182950@timeedit.evolvera.se", "date": calendar.Date("20041028"),
            "begin": calendar.Time("100000"), "end": calendar.Time("120000"), "location": "", "summary": "5B1506.Ö D2D I3KSI I2FIM Q31 Q32 Q33 Q34"})

        data = ["BEGIN:VCALENDAR", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-TIMEZONE;VALUE=TEXT:Europe/Stockholm",
            "X-WR-CALNAME;VALUE=TEXT:TimeEdit", "VERSION:2.0", "PRODID:-//Evolvera AB\, //TimeEdit Global//EN",
            "BEGIN:VEVENT","DTSTAMP:20040204T154631","SUMMARY:X3X X4X 9E1338.Le E34 ---","DTSTART:20041129T170000",
            "DTEND:20041129T210000","UID:20040809T103009-26770@timeedit.evolvera.se","END:VEVENT",
            "BEGIN:VEVENT","DTSTAMP:20040423T170829","SUMMARY:4D1225.Sem X3X","DTSTART:20040923T130000",
            "DTEND:20040923T150000","UID:20040809T103009-195910@timeedit.evolvera.se","END:VEVENT",            
            "BEGIN:VEVENT","DTSTAMP:20040416T102855","SUMMARY:5B1506.Ö D2D I3KSI I2FIM Q31 Q32 Q33 Q34",
            "DTSTART:20041028T100000","DTEND:20041028T120000","UID:20040809T160814-182950@timeedit.evolvera.se",
            "END:VEVENT","END:VCALENDAR"]
            
        self.failUnlessListsEqual(vcalendar.Reader().read(data), events)

# -----------------------------------------------------------
class WriterTest(xunittest.TestCase):
    def testWrite(self):
        timetable.courselist.clear()
        timetable.courselist.addCourse("2B1345", "DigEl", 616, 2)
        timetable.courselist.addCourse("DSV:L/9E1363", "Kommunikation", 429, 5)
        timetable.courselist.addCourse("5B1113", "Matte", 754, 0)

        events = []
        events.append(timetable.Event("DAISYKTH1000", calendar.Date("20040301"), calendar.Time("110000"),
            calendar.Time("130000"), "Sal A", "Föreläsning 1 Sal A - 5B1113"))
        events.append(timetable.Event("DAISYKTH1001", calendar.Date("20040414"), calendar.Time("093000"),
            calendar.Time("120000"), "540", "Lektion 3 grp 2 540 - 2B1345"))
        events.append(timetable.Event("DAISYKTH1002", calendar.Date("20040414"), calendar.Time("153000"),
            calendar.Time("180000"), "Aulan", "Introduktion Aulan - DSV:L/9E1363"))
        events.append(timetable.Event("DAISYKTH1003", calendar.Date("20040416"), calendar.Time("100000"),
            calendar.Time("120000"), "Aulan", "Föreläsning 1 Aulan - DSV:L/9E1363"))
            
        data = "BEGIN:VCALENDAR\nVERSION:1.0\nPRODID:-//cda//NONSGML Schema//SV\n" +\
            "BEGIN:VEVENT\nUID:DAISYKTH1000\nDTSTART:20040301T100000Z\nDTEND:20040301T120000Z\n" +\
            "SUMMARY:Matte F1\nLOCATION:Sal A\nEND:VEVENT\n" +\
            "BEGIN:VEVENT\nUID:DAISYKTH1001\nDTSTART:20040414T073000Z\nDTEND:20040414T100000Z\n" +\
            "SUMMARY:DigEl Lekt3 grp 2\nLOCATION:540\nEND:VEVENT\n" +\
            "BEGIN:VEVENT\nUID:DAISYKTH1002\nDTSTART:20040414T133000Z\nDTEND:20040414T160000Z\n" +\
            "SUMMARY:Kommunikation Intro\nLOCATION:Aulan\nEND:VEVENT\n" +\
            "BEGIN:VEVENT\nUID:DAISYKTH1003\nDTSTART:20040416T080000Z\nDTEND:20040416T100000Z\n" +\
            "SUMMARY:Kommunikation F1\nLOCATION:Aulan\nEND:VEVENT\n" +\
            "END:VCALENDAR"

        vcalendar.Writer("-//cda//NONSGML Schema//SV").write(events, "_test")
        self.failUnlessEqual(file("_test").read(), data)
        
        import os
        os.remove("_test")

# -----------------------------------------------------------
xunittest.run()
        
