#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

from i18n import *
setLanguage("en")

import timetable
import calendar
import xunittest

# -----------------------------------------------------------
class CourseTest(xunittest.TestCase):
    def testInit(self):
        c = timetable.Course("*:59/2I1140", "Artificiell intelligens", 934, 1, "20051")
        self.failUnlessEqual(c.code, "*:59/2I1140")
        self.failUnlessEqual(c.name, "Artificiell intelligens")
        self.failUnlessEqual(c.id, 934)
        self.failUnlessEqual(c.group, "1")
        self.failUnlessEqual(c.getTerm(), "VT05")

        c = timetable.Course("2C1224", "Projektstyrning")
        self.failUnlessEqual(c.code, "2C1224")
        self.failUnlessEqual(c.id, "2C1224")
        self.failUnlessEqual(c.name, "Projektstyrning")
        self.failUnlessEqual(c.group, "")
        
    def testEqual(self):
        c1 = timetable.Course("*:59/2I1140", "Artificiell intelligens", 934)
        c2 = timetable.Course("*:59/2I1140", "Artificiell intelligens", 809)
        c3 = timetable.Course("5B1116", "Matematisk statistik", group="a")
        c4 = timetable.Course("5B1116", "MatStat", group="c")
        self.failIfEqual(c1, c3)
        self.failIfEqual(c1, c2)
        self.failUnlessEqual(c3, c4)
        self.failUnlessEqual(c1, c1)
        
    def testHasCode(self):
        c = timetable.Course("*:36/2I1225/2I1374/2I1190", "DSV-kurs")
        self.failUnless(c.hasCode("*:36/2I1225/2I1374/2"))

        c = timetable.Course("5B1506 IT", "Matte nånting")
        self.failUnless(c.hasCode("5B1506 ME"))

        c = timetable.Course("*:59/2I1140", "Artificiell intelligens")
        self.failIf(c.hasCode("6B3023"))

    def testIsDaisyOrTimeEdit(self):
        c = timetable.Course("*:59/2I1140", "Artificiell intelligens", 809)
        self.failIf(c.isTimeEdit())
        self.failUnless(c.isDaisy())

        c = timetable.Course("5B1116", "Matematisk statistik")
        self.failIf(c.isDaisy())
        self.failUnless(c.isTimeEdit())

    def testGetTerm(self):
        c = timetable.Course("*:59/2I1140", "Artificiell intelligens", term="20051")
        self.failUnlessEqual(c.getTerm(), "VT05")

        c = timetable.Course("*:59/2I1140", "Artificiell intelligens", term="20042")
        self.failUnlessEqual(c.getTerm(), "HT04")

# -----------------------------------------------------------
class CourseListTest(xunittest.TestCase):

    courselist = None
    courses = []

    def setUp(self):
        self.courses = []
        self.courses.append(timetable.Course("2B1345", "DigEl", group="3"))
        self.courses.append(timetable.Course("*:59", "DSV-mysko", 931))
        self.courses.append(timetable.Course("DSV:L/9E1363", "Kommunikation", 429, group="5"))
        self.courses.append(timetable.Course("5B1113 IT", "Matte"))

        self.courselist = timetable.CourseList()
        self.courselist.courses.append(timetable.Course("2B1345", "DigEl"))
        self.courselist.courses.append(timetable.Course("*:59", "DSV-mysko", 931))
        self.courselist.courses.append(timetable.Course("DSV:L/9E1363", "Kommunikation", 429))
        self.courselist.courses.append(timetable.Course("5B1113 IT", "Matte"))

    def testClearAndEmpty(self):
        self.courselist.clear()
        self.failIf(self.courselist.courses)
        self.failUnless(self.courselist.isEmpty())
        
    def testDaisyCourseIDs(self):
        self.failUnlessListsEqual([931,429], self.courselist.getAllDaisyCourseIDs())

    def testTimeEditCourseIDs(self):
        self.failUnlessListsEqual(["2B1345", "5B1113 IT"], self.courselist.getAllTimeEditCourseIDs())

    def testGetAllMatchingName(self):
        courses = self.courselist.getAllMatchingName("DSV")
        self.failUnlessEqual(len(courses), 1)
        self.failUnlessEqual(courses[0].code, "*:59")

        courses = self.courselist.getAllMatchingName("qwerty")
        self.failIf(len(courses))

    def testGetAllMatchingCode(self):
        courses = self.courselist.getAllMatchingCode("DSV")
        self.failUnlessEqual(len(courses), 1)
        self.failUnlessEqual(courses[0].code, "DSV:L/9E1363")

        courses = self.courselist.getAllMatchingCode("qwerty")
        self.failIf(len(courses))

    def tstAddCourses(self):
        self.courselist.clear()
        for course in self.courses:
            code = course.code
            name = course.name
            id = course.id
            group = course.group
            self.courselist.addCourse(code, name, id, group)

        self.failUnlessEqual(self.courselist.courses, self.courses)

        count = len(self.courselist.courses)
        self.courselist.addCourse("5B1113 IT", "Matematik")
        self.failUnlessEqual(count, len(self.courselist.courses))
        self.failUnlessEqual(self.courselist.getCourseName("5B1113 IT"), "Matematik")

        self.courses.append(timetable.Course("9B1111", "X"))
        self.courselist.addCourse(timetable.Course("9B1111", "X"))
        self.failUnlessEqual(self.courses, self.courselist.courses)

    def tstRemoveCourse(self):
        self.courselist.removeCourse("DSV:L/9E1363")
        self.courses.remove(timetable.Course("DSV:L/9E1363", "Kommunikation", 429, 5))

        self.failUnlessListsEqual(self.courselist.courses, self.courses)
        self.failUnlessRaises(ValueError, self.courselist.removeCourse, "abc")

    def testGetCourse(self):
        course5B1113 = timetable.Course("5B1113 IT", "Matte")
        course9E1363 = timetable.Course("DSV:L/9E1363", "Kommunikation", 429)

        self.failUnlessEqual(self.courselist.getCourse(429), course9E1363)
        self.failUnlessEqual(self.courselist.getCourse("5B1113 IT"), course5B1113)
        self.failUnlessRaises(ValueError, self.courselist.getCourse, "abc")

# -----------------------------------------------------------
class TimeTableTest: #(xunittest.TestCase):
    def setUp(self):
        self.events = {}
        self.timetable = timetable.TimeTable()
        self.timetable.updated = calendar.DateTime("20040530")
        self.updated = calendar.DateTime("20040530")

        timetable.courselist.clear()
        timetable.courselist.addCourse("2B1345", "DigEl", 616, 2)
        timetable.courselist.addCourse("*:59", "DSV-mysko", 931, 0)
        timetable.courselist.addCourse("DSV:L/9E1363", "Kommunikation", 429, 5)
        timetable.courselist.addCourse("5B1113", "Matte", 754, 0)

        self.events["DAISYKTH1000"] = timetable.Event("DAISYKTH1000", calendar.Date("20040301"),
            calendar.Time("110000"), calendar.Time("130000"), "Sal A", "Föreläsning 1 Sal A - 5B1113")
        self.events["DAISYKTH1001"] = timetable.Event("DAISYKTH1001", calendar.Date("20040414"), calendar.Time("093000"),
            calendar.Time("120000"), "540", "Lektion 3 grp 2 540 - 2B1345")
        self.events["DAISYKTH1002"] = timetable.Event("DAISYKTH1002", calendar.Date("20040414"), calendar.Time("153000"),
            calendar.Time("180000"), "Aulan", "Introduktion Aulan - DSV:L/9E1363")
        self.events["DAISYKTH1003"] = timetable.Event("DAISYKTH1003", calendar.Date("20040416"), calendar.Time("100000"),
            calendar.Time("120000"), "Aulan", "Föreläsning 1 Aulan - DSV:L/9E1363")

        self.timetable.eventlist.events["DAISYKTH1000"] = timetable.Event("DAISYKTH1000", calendar.Date("20040301"), calendar.Time("110000"),
            calendar.Time("130000"), "Sal A", "Föreläsning 1 Sal A - 5B1113")
        self.timetable.eventlist.events["DAISYKTH1001"] = timetable.Event("DAISYKTH1001", calendar.Date("20040414"), calendar.Time("093000"),
            calendar.Time("120000"), "540", "Lektion 3 grp 2 540 - 2B1345")
        self.timetable.eventlist.events["DAISYKTH1002"] = timetable.Event("DAISYKTH1002", calendar.Date("20040414"), calendar.Time("153000"),
            calendar.Time("180000"), "Aulan", "Introduktion Aulan - DSV:L/9E1363")
        self.timetable.eventlist.events["DAISYKTH1003"] = timetable.Event("DAISYKTH1003", calendar.Date("20040416"), calendar.Time("100000"),
            calendar.Time("120000"), "Aulan", "Föreläsning 1 Aulan - DSV:L/9E1363")

    def testEmpty(self):
        self.failIf(self.timetable.isEmpty())
        self.timetable.eventlist.clear()
        self.failUnless(self.timetable.isEmpty())
        
    def testEvent(self):
        self.failUnlessEqual(self.timetable.getEvent("DAISYKTH1003"),
            timetable.Event("DAISYKTH1003", calendar.Date("20040416"), calendar.Time("100000"),
            calendar.Time("120000"), "Aulan", "Föreläsning 1 Aulan - DSV:L/9E1363"))
        self.failUnlessEqual(self.timetable.getEvent("DAISYKTH1001"),
            timetable.Event("DAISYKTH1001", calendar.Date("20040414"), calendar.Time("093000"),
            calendar.Time("120000"), "540", "Lektion 3 grp 2 540 - 2B1345"))
        self.failUnlessRaises(ValueError, self.timetable.getEvent, "abc")
        
    def testAllGroups(self):
        self.failUnlessEqual(self.timetable.getAllGroups("2B1345"), [2])
        self.failIf(self.timetable.getAllGroups("5B1113"))
        self.failUnlessRaises(ValueError, self.timetable.getAllGroups, "abc")

    def testEventsForDate(self):
        events = []
        events.append(timetable.Event("DAISYKTH1001", calendar.Date("20040414"), calendar.Time("093000"),
            calendar.Time("120000"), "540", "Lektion 3 grp 2 540 - 2B1345"))
        events.append(timetable.Event("DAISYKTH1002", calendar.Date("20040414"), calendar.Time("153000"),
            calendar.Time("180000"), "Aulan", "Introduktion Aulan - DSV:L/9E1363"))

        self.failUnlessListsEqual(self.timetable.getEventsForDate(calendar.Date("20040414")), events)
        
    def testEventsForDateRange(self):
        events = []
        events.append(timetable.Event("DAISYKTH1000", calendar.Date("20040301"), calendar.Time("110000"),
            calendar.Time("130000"), "Sal A", "Föreläsning 1 Sal A - 5B1113"))
        events.append(timetable.Event("DAISYKTH1001", calendar.Date("20040414"), calendar.Time("093000"),
            calendar.Time("120000"), "540", "Lektion 3 grp 2 540 - 2B1345"))
        events.append(timetable.Event("DAISYKTH1002", calendar.Date("20040414"), calendar.Time("153000"),
            calendar.Time("180000"), "Aulan", "Introduktion Aulan - DSV:L/9E1363"))

        self.failUnlessListsEqual(self.timetable.getEventsForDateRange(calendar.Date("20040301"),
            calendar.Date("20040414")), events)

    def testRemoveCourseEvents(self):
        remaining = []
        for event in self.events.values():
            if event.course != "DSV:L/9E1363":
                remaining.append(event)
                
        self.timetable.removeCourseEvents("DSV:L/9E1363")
        self.failUnlessListsEqual(self.timetable.eventlist.getAll(), remaining)

    def testLoadSave(self):
        events = []
        events.extend(self.timetable.eventlist.getAll())
        updated = self.timetable.updated
        courses = []
        courses.extend(timetable.courselist.courses)

        self.timetable.save("_test")
        timetable.courselist.clear()
        self.timetable.clear()
        self.timetable.updated = None
        self.timetable.load("_test")
        
        import os
        os.remove("_test")
        # testa save till skrivskyddad fil
        
        self.failUnlessListsEqual(self.timetable.eventlist.getAll(), events)
        self.failUnlessListsEqual(timetable.courselist.courses, courses)
        self.failUnlessEqual(self.timetable.updated, updated)
        
# -----------------------------------------------------------
class EventTest: #(xunittest.TestCase):
    def setUp(self):
        timetable.courselist.clear()
        timetable.courselist.addCourse("5B1506 IT", "MatStat", 123)
        timetable.courselist.addCourse("DSV2:B", "DSV-mysko", 123)
        timetable.courselist.addCourse("5B1506 ME", "MatStat", 123)
        timetable.courselist.addCourse("2I1140", "AI", 123)
    
    def testInitFromDict(self):
        event = timetable.Event()
        event.setID(333)
        event.date = calendar.Date("20031109")
        event.begin = calendar.Time("133000")
        event.end = calendar.Time("160000")
        event.location = "E51"
        event.course = "2C1445"
        event.type = "Föreläsning"
        event.group = 1
        event.seriesno = 7
        
        eventdict = {"id": 333, "date": "20031109", "begin": "133000", "end": "160000",
            "location": "E51", "course": "2C1445", "type": "Föreläsning", "group": 1, "seriesno": 7}
        self.failUnlessEqual(timetable.Event(eventdict), event)
    
        event = timetable.Event()
        event.setID("DAISYKTH")
        event.date = calendar.Date("20040901")
        event.begin = calendar.Time("124500")
        event.end = calendar.Time("130000")
        event.location = "Sal B"
        event.course = timetable.courselist.getCourse("2I1140")
        event.type = "Introduktion"
        event.group = 0
        event.seriesno = 0
        
        eventdict = {"id": "DAISYKTH", "date": "20040901", "begin": "124500", "end": "130000",
            "location": "Sal B", "course": "2I1140", "type": "Introduktion", "group": 0, "seriesno": 0}
        self.failUnlessEqual(timetable.Event(eventdict), event)

        eventdict = {"id": "DAISYKTH", "date": "20040901", "begin": "124500", "end": "130000",
            "location": "Sal B", "summary": "Introduktion Sal B - 2I1140"}
        self.failUnlessEqual(timetable.Event(eventdict), event)

        event = timetable.Event()
        event.setID("20040829T172813-177840@timeedit.evolvera.se")
        event.date = calendar.Date("20040901")
        event.begin = calendar.Time("124500")
        event.end = calendar.Time("130000")
        event.location = "F3"
        event.course = "DSV2:B"
        event.type = "Seminarium"

        eventdict = {"id": "20040829T172813-177840@timeedit.evolvera.se", "date": "20040901",
            "begin": "124500", "end": "130000", "location": "", "summary": "DSV2:B.Sem X3X F3"}
        self.failUnlessEqual(timetable.Event(eventdict), event)

    def testInitAndString(self):
        event = timetable.Event("DAISYKTH", location="539", summary="Övning 1 grp 1 539 - 5B1506")
        self.failUnlessEqual(str(event), "MatStat Ö1 grp 1 (539)")

        event = timetable.Event("DAISYKTH", location="215,313,314,Forum, Kista", summary="Salsskrivning 215,313,314,Forum, Kista - DSV2:B")
        self.failUnlessEqual(str(event), "DSV-mysko Tenta (215,313,314,Forum, Kista)")

        event = timetable.Event("DAISYKTH", location="538", summary="Lektion 26 538 - 5B1506 ME")
        self.failUnlessEqual(str(event), "MatStat Lekt26 (538)")

        event = timetable.Event("timeedit.evolvera.se", summary="M4MEK T4MEK V4BKO 5B1506.WS V26t ---")
        self.failUnlessEqual(str(event), "MatStat WS (V26t)")
        
        event = timetable.Event("timeedit.evolvera.se", summary="DSV2:B.L D4D E4E F4F 5V5Vio")
        self.failUnlessEqual(str(event), "DSV-mysko Labb (5V5Vio)")

        event = timetable.Event("timeedit.evolvera.se", summary="DSV2:B.Sem X3X")
        self.failUnlessEqual(str(event), "DSV-mysko Sem")

        event = timetable.Event("timeedit.evolvera.se", summary="D2D I2FIM I3KSI 5B1506.TEN E31 E32 E33 E34 E35 E36 V32 V33 V...")
        self.failUnlessEqual(str(event), "MatStat Tenta (E31,E32,E33,E34,E35,E36,V32,V33)")

    def testCopy(self):
        event = timetable.Event("DAISYKTH", location="539", summary="Övning 1 grp 1 539 - 5B1506")
        copy = timetable.Event()
        copy.copy(event)
        self.failUnlessEqual(event, copy)

# -----------------------------------------------------------
class EventListTest: #(xunittest.TestCase):
    def setUp(self):
        self.eventlist = timetable.EventList([{"id": 1, "location": "1"},
            {"id": 2, "location": "2"}, {"id": 3, "location": "3"}])

        self.events = {}
        self.events[1] = timetable.Event(1, location="1")
        self.events[2] = timetable.Event(2, location="2")
        self.events[3] = timetable.Event(3, location="3")
    
    def testInit(self):
        self.failUnlessEqual(self.eventlist.events, self.events)
    
    def testAdd(self):
        self.events[6] = timetable.Event(6, location="6")
        self.eventlist.addEvent(timetable.Event(6, location="6"))
        
        self.failUnlessEqual(self.eventlist.events, self.events)

        self.events[33] = timetable.Event(33, location="33")
        self.eventlist.addEvent(timetable.Event(33, location="33"))
        
        self.failUnlessEqual(self.eventlist.events, self.events)
        
    def testRemove(self):
        del self.events[2]
        self.eventlist.removeEvent(2)
        self.failUnlessEqual(self.eventlist.events, self.events)
        
# -----------------------------------------------------------
class TimeTableComparatorTest: #(xunittest.TestCase):

    def testAdded(self):
        events = []
        events.append(timetable.Event("DAISYKTH1000", calendar.Date("20040301"), calendar.Time("110000"),
            calendar.Time("130000"), "Sal A", "Föreläsning 1 Sal A - 5B1113"))
        events.append(timetable.Event("DAISYKTH1001", calendar.Date("20040414"), calendar.Time("093000"),
            calendar.Time("120000"), "540", "Lektion 3 grp 2 540 - 2B1345"))
        events.append(timetable.Event("DAISYKTH1002", calendar.Date("20040414"), calendar.Time("153000"),
            calendar.Time("180000"), "Aulan", "Introduktion Aulan - DSV:L/9E1363"))
        events.append(timetable.Event("DAISYKTH1003", calendar.Date("20040416"), calendar.Time("100000"),
            calendar.Time("120000"), "Aulan", "Föreläsning 1 Aulan - DSV:L/9E1363"))
        events.append(timetable.Event("DAISYKTH1004", calendar.Date("20040419"), calendar.Time("080000"),
            calendar.Time("120000"), "Sal B", "Föreläsning 2 Sal B - DSV:L/9E1363"))
            
        self.failUnlessEqual(self.timetable.getAdded(events), ["DAISYKTH1004"])
        
    def testRemoved(self):
        events = []
        events.append(timetable.Event("DAISYKTH1000", calendar.Date("20040301"), calendar.Time("110000"),
            calendar.Time("130000"), "Sal A", "Föreläsning 1 Sal A - 5B1113"))
        events.append(timetable.Event("DAISYKTH1002", calendar.Date("20040414"), calendar.Time("153000"),
            calendar.Time("180000"), "Aulan", "Introduktion Aulan - DSV:L/9E1363"))
        events.append(timetable.Event("DAISYKTH1003", calendar.Date("20040416"), calendar.Time("100000"),
            calendar.Time("120000"), "Aulan", "Föreläsning 1 Aulan - DSV:L/9E1363"))
        events.append(timetable.Event("DAISYKTH1004", calendar.Date("20040419"), calendar.Time("080000"),
            calendar.Time("120000"), "Sal B", "Föreläsning 2 Sal B - DSV:L/9E1363"))
            
        self.failUnlessEqual(self.timetable.getRemoved(events), ["DAISYKTH1001"])

    def testChanged(self):
        events = []
        events.append(timetable.Event("DAISYKTH1000", calendar.Date("20040301"), calendar.Time("110000"),
            calendar.Time("130000"), "Sal A", "Föreläsning 1 Sal A - 5B1113"))
        events.append(timetable.Event("DAISYKTH1002", calendar.Date("20040414"), calendar.Time("160000"),
            calendar.Time("180000"), "Aulan", "Introduktion Aulan - DSV:L/9E1363"))
        events.append(timetable.Event("DAISYKTH1003", calendar.Date("20040415"), calendar.Time("100000"),
            calendar.Time("120000"), "Aulan", "Föreläsning 1 Aulan - DSV:L/9E1363"))
        events.append(timetable.Event("DAISYKTH1004", calendar.Date("20040419"), calendar.Time("080000"),
            calendar.Time("120000"), "Sal B", "Föreläsning 2 Sal B - DSV:L/9E1363"))
            
        self.failUnlessListsEqual(self.timetable.getChanged(events),
            ["DAISYKTH1002", "DAISYKTH1003"])

# -----------------------------------------------------------
class HTMLExporterTest: #(xunittest.TestCase):
    def testExport(self):
        timetable.courselist.clear()
        timetable.courselist.addCourse("5B1506", "MatStat", 123)
        timetable.courselist.addCourse("DSV2:B", "DSV-mysko", 123)

        table = timetable.TimeTable()
        exporter = timetable.HTMLExporter()
        
        event = timetable.Event()
        event.setID(1)
        event.date = calendar.Date("20040901")
        event.begin = calendar.Time("124500")
        event.end = calendar.Time("130000")
        event.location = "F3"
        event.course = "DSV2:B"
        event.type = "Seminarium"
        table.addEvent(event)

        event = timetable.Event()
        event.setID(2)
        event.date = calendar.Date("20040901")
        event.begin = calendar.Time("130000")
        event.end = calendar.Time("150000")
        event.location = "Sal B"
        event.course = "5B1506"
        event.type = "Lektion"
        table.addEvent(event)

        event = timetable.Event()
        event.setID(3)
        event.date = calendar.Date("20040903")
        event.begin = calendar.Time("090000")
        event.end = calendar.Time("110000")
        event.location = "Aulan"
        event.course = "5B1506"
        event.type = "Övning"
        event.seriesno = 3
        table.addEvent(event)

        event = timetable.Event()
        event.setID(4)
        event.date = calendar.Date("20040906")
        event.begin = calendar.Time("080000")
        event.end = calendar.Time("100000")
        event.location = "540"
        event.course = "5B1506"
        event.type = "Seminarium"
        event.seriesno = 3
        table.addEvent(event)

        event = timetable.Event()
        event.setID(5)
        event.date = calendar.Date("20040908")
        event.begin = calendar.Time("170000")
        event.end = calendar.Time("210000")
        event.location = "F3"
        event.course = "DSV2:B"
        event.type = "Föreläsning"
        event.seriesno = 6
        table.addEvent(event)

        event = timetable.Event()
        event.setID(6)
        event.date = calendar.Date("20040902")
        event.begin = calendar.Time("120000")
        event.end = calendar.Time("140000")
        event.location = "F3"
        event.course = "DSV2:B"
        event.type = "Seminarium"
        event.active = False
        table.addEvent(event)

        exporter.export("_test", table, calendar.Date("20040831"), calendar.Date("20040909"))
        exporteddata = file("_test").read()
        
        self.failUnlessEqual(exporteddata, """<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.1//EN'
            'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd'>
            <html xmlns='http://www.w3.org/1999/xhtml' xml:lang='sv'>
            <head>
            <title>Schema</title>
            <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1' />
            <meta name='generator' content='Schema' />
            <link rel='stylesheet' type='text/css' href='timetable-html.css' />
            </head>
            <body><h1>Schema</h1>
            <div class='week'><h2>Vecka 36</h2><div class='day'><h3>Mån 30/8</h3></div><div class='day'><h3>Tis 31/8</h3></div><div class='day'><h3>Ons 1/9</h3><div class='event'>12:45-13:00: DSV-mysko Sem (F3)</div><div class='event'>13:00-15:00: MatStat Lekt (Sal B)</div></div><div class='day'><h3>Tor 2/9</h3></div><div class='day'><h3>Fre 3/9</h3><div class='event'>09:00-11:00: MatStat Ö3 (Aulan)</div></div></div>
<div class='week'><h2>Vecka 37</h2><div class='day'><h3>Mån 6/9</h3><div class='event'>08:00-10:00: MatStat Sem3 (540)</div></div><div class='day'><h3>Tis 7/9</h3></div><div class='day'><h3>Ons 8/9</h3><div class='event'>17:00-21:00: DSV-mysko F6 (F3)</div></div><div class='day'><h3>Tor 9/9</h3></div><div class='day'><h3>Fre 10/9</h3></div></div>
</body></html>""")

        import os
        os.remove("_test")

# -----------------------------------------------------------
class VCalendarExporterTest: #(xunittest.TestCase):
    def testExport(self):
        timetable.courselist.clear()
        timetable.courselist.addCourse("5B1506", "MatStat", 123)
        timetable.courselist.addCourse("DSV2:B", "DSV-mysko", 123)

        table = timetable.TimeTable()
        exporter = timetable.VCalendarExporter()
        
        event = timetable.Event()
        event.setID(1)
        event.date = calendar.Date("20040901")
        event.begin = calendar.Time("124500")
        event.end = calendar.Time("130000")
        event.location = "F3"
        event.course = "DSV2:B"
        event.type = "Seminarium"
        table.addEvent(event)

        event = timetable.Event()
        event.setID(2)
        event.date = calendar.Date("20040901")
        event.begin = calendar.Time("130000")
        event.end = calendar.Time("150000")
        event.location = "Sal B"
        event.course = "5B1506"
        event.type = "Lektion"
        table.addEvent(event)

        event = timetable.Event()
        event.setID(3)
        event.date = calendar.Date("20040903")
        event.begin = calendar.Time("090000")
        event.end = calendar.Time("110000")
        event.location = "Aulan"
        event.course = "5B1506"
        event.type = "Övning"
        event.seriesno = 3
        table.addEvent(event)

        event = timetable.Event()
        event.setID(4)
        event.date = calendar.Date("20040906")
        event.begin = calendar.Time("080000")
        event.end = calendar.Time("100000")
        event.location = "540"
        event.course = "5B1506"
        event.type = "Seminarium"
        event.seriesno = 3
        table.addEvent(event)

        event = timetable.Event()
        event.setID(5)
        event.date = calendar.Date("20040908")
        event.begin = calendar.Time("170000")
        event.end = calendar.Time("210000")
        event.location = "F3"
        event.course = "DSV2:B"
        event.type = "Föreläsning"
        event.seriesno = 6
        table.addEvent(event)

        event = timetable.Event()
        event.setID(6)
        event.date = calendar.Date("20040902")
        event.begin = calendar.Time("120000")
        event.end = calendar.Time("140000")
        event.location = "F3"
        event.course = "DSV2:B"
        event.type = "Seminarium"
        event.active = False
        table.addEvent(event)

        exporter.export("_test", table, calendar.Date("20040831"), calendar.Date("20040909"))
        exporteddata = file("_test").read()
        
        self.failUnlessEqual(exporteddata, """BEGIN:VCALENDAR
VERSION:1.0
PRODID:-//cda//NONSGML Schema//SV
BEGIN:VEVENT
UID:1
DTSTART:20040901T104500Z
DTEND:20040901T110000Z
SUMMARY:DSV-mysko Sem
LOCATION:F3
END:VEVENT
BEGIN:VEVENT
UID:2
DTSTART:20040901T110000Z
DTEND:20040901T130000Z
SUMMARY:MatStat Lekt
LOCATION:Sal B
END:VEVENT
BEGIN:VEVENT
UID:3
DTSTART:20040903T070000Z
DTEND:20040903T090000Z
SUMMARY:MatStat Ö3
LOCATION:Aulan
END:VEVENT
BEGIN:VEVENT
UID:4
DTSTART:20040906T060000Z
DTEND:20040906T080000Z
SUMMARY:MatStat Sem3
LOCATION:540
END:VEVENT
BEGIN:VEVENT
UID:5
DTSTART:20040908T150000Z
DTEND:20040908T190000Z
SUMMARY:DSV-mysko F6
LOCATION:F3
END:VEVENT
END:VCALENDAR""")

        import os
        os.remove("_test")

# -----------------------------------------------------------
xunittest.run()
