# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import calendar
import daisy
import timeedit
import error
from i18n import *

# -----------------------------------------------------------
class CourseList:
    "Lista med kurser"

    def __init__(self):
        self.courses = []

    def clear(self):
        self.courses = []
        
    def clearDaisyCourses(self):
        for course in self.getAllDaisyCourseCodes():
            self.removeCourse(course)
        
    def clearTimeEditCourses(self):
        for course in self.getAllTimeEditCourseCodes():
            self.removeCourse(course)

    def isEmpty(self):
        return self.courses == []
    
    def getCourseType(self, code):
        if code in self.getAllDaisyCourseCodes():
            return "Daisy"
        else:
            return "TimeEdit"        

    def addCourse(self, codeorcourse, name="", id=0, group=0):
        """
            Lägger till en kurs eller skriver över befintlig om samma kod

            Det kan alltså finnas flera kurser med samma kurs/moment-ID,
            men inte med samma kurskod.
        """

        if isinstance(codeorcourse, Course):
            try:
                self.courses.remove(codeorcourse)
            except ValueError:
                pass
            
            self.courses.append(codeorcourse)
        else:
            try:
                self.courses.remove(self.getCourse(codeorcourse))
            except ValueError:
                pass
    
            self.courses.append(Course(codeorcourse, name, id, group))
        
    def removeCourse(self, code):
        "Tar bort en kurs ur listan"
        self.courses.remove(self.getCourse(code))
        global timetable
        timetable.removeCourseEvents(code)

    def getCourse(self, code):
        "Returnerar en kurs definierad av kod"

        for course in self.courses:
            if course == code: return course

        raise ValueError(U_("Kursen") + " " + U_("finns inte") + " (" + U_("kod") + " " + str(code) + ")")

    def getCourseName(self, code):
        "Returnerar namnet (ev. användardefinierat) på en kurs"
        return self.getCourse(code).name

    def setCourseName(self, code, name):
        self.getCourse(code).name = name

    def getCourseGroup(self, code):
        "Returnerar vald grupp för aktuell kurs"
        return self.getCourse(code).group

    def setCourseGroup(self, code, group):
        self.getCourse(code).group = int(group)

    def getCourseID(self, code):
        "Returnerar kurs-id på en kurs"
        return self.getCourse(code).id

    def setCourseID(self, code, id):
        self.getCourse(code).id = int(id)

    def getAllDaisyCourseIDs(self):
        ids = []
        for course in self.getAllDaisyCourseCodes():
            ids.append(self.getCourseID(course))

        return ids

    def getAllDaisyCourseCodes(self):
        codes = []
        for course in self.courses:
            if course.id: codes.append(course.code)

        return codes

    def getAllTimeEditCourseCodes(self):
        codes = []
        for course in self.courses:
            if not course.id: codes.append(course.code)

        return codes

    def getAllDaisyCourses(self):
        codes = self.getAllDaisyCourseCodes()
        courses = []
        for code in codes:
            courses.append(self.getCourse(code))

        return courses

    def getAllTimeEditCourses(self):
        codes = self.getAllTimeEditCourseCodes()
        courses = []
        for code in codes:
            courses.append(self.getCourse(code))

        return courses

# -----------------------------------------------------------
class TimeTable:
    "Ett schema (dvs en samling schemalagda händelser)"

    def __init__(self):
        self.eventlist = EventList()
        self.updated = None
        self.courselist = CourseList()
        self.username = ""
        
    def clear(self):
        self.eventlist.clear()
        self.updated = None
        
    def addEvent(self, event):
        self.eventlist.addEvent(event)

    def getAllDaisyEvents(self):
        events = []
        for event in self.eventlist.getAll():
            if courselist.getCourseType(event.course) == "Daisy":
                events.append(event)
        
        return events
        
    def getAllTimeEditEvents(self):
        events = []
        for event in self.eventlist.getAll():
            if courselist.getCourseType(event.course) == "TimeEdit":
                events.append(event)

        return events
    
    def clearEventsFromSource(self, source):
        if source == "Daisy":
            remove = self.getAllDaisyEvents()
            for event in remove:
                self.eventlist.removeEvent(event.getID())
        elif source == "TimeEdit":
            remove = self.getAllTimeEditEvents()
            for event in remove:
                self.eventlist.removeEvent(event.getID())
        else:
            raise ValueError(U_("Felaktig kalla") + " " + source)
        
    def isEmpty(self):
        return self.eventlist.isEmpty()

    def importData(self, input, source):
        "Importerar data från fil eller lista -- ersätter aktuellt schema"
        import vcalendar
        self.clearEventsFromSource(source)
        newevents = vcalendar.Reader().read(input)
        if newevents:
            self.eventlist.addEvents(newevents)
            self.updated = calendar.Date()
        
    def getEvent(self, id):
        return self.eventlist.getEvent(id)

    def getAllGroups(self, code):
        "Returnerar alla möjliga grupper för en viss kurs"

        groups = []
        events = self.getAllEventsForCourse(code)
        for event in events:
            if event.group and str(event.group) not in groups:
                groups.append(str(event.group))

        return groups

    def getAllEventsForCourse(self, code):
        "Returnerar alla händelser för en viss kurs, utan hänsyn till gruppval"
        
        events = []
        coursefound = False
        for event in self.eventlist.getAll():
            if event.course == code:
                coursefound = True
                events.append(event)

        if not coursefound:
            raise ValueError(U_("Kursen") + " " + str(code) + " " + U_("finns inte"))
            
        return events

    def getEventsForDate(self, date):
        events = []
        for event in self.eventlist.getAll():
            if event.date == date and event.isGroupChosen():
                events.append(event)

        return events

    def getEventsForDateRange(self, fromdate, todate):
        date = calendar.Date(fromdate)
        events = []
        while date <= todate:
            events.extend(self.getEventsForDate(date))
            date += 1
        return events

    def removeCourseEvents(self, course):
        "Tar bort alla händelser för en viss kurs"

        try:
            remove = self.getAllEventsForCourse(course)
            for event in remove:
                self.eventlist.removeEvent(event.getID())
        except ValueError:
            return # redan borttaget

    def load(self, filename = ""):
        "Läser in schemat från en INI-liknande fil"

        import ConfigParser # för undantag
        import configfileparser
        import settings
        import os.path

        global courselist
        courselist.clear()
        self.clear()

        if not filename:
            filename = settings.timetablefile
        if not os.path.exists(filename):
            return # ger inget felmeddelande

        config = configfileparser.ConfigParserX()
        try:
            config.readfp(file(filename))
        except IOError:
            raise error.ReadError(U_("Kan inte lasa fran fil"), filename)

        # läser först in inställningarna och kurserna ...
        for section in config.sections():
            if section == "main":
                self.updated = calendar.Date(config.get(section, "updated"))
                try:
                    self.username = config.get(section, "username")
                except ConfigParser.NoOptionError:
                    pass

            elif section == "courses":
                pairs = config.items(section)
                for pair in pairs:
                    code = pair[0]
                    data = pair[1].split("|")
                    courselist.addCourse(code, data[0], int(data[1]), int(data[2]))

        # ... och därefter alla händelser som beror på de inlästa kurserna
        for section in config.sections():
            if section != "main" and section != "courses":
                event = Event()

                event.setID(section)
                try:
                    event.location = config.get(section, "location")
                    event.date = calendar.Date(config.get(section, "date"))
                    event.begin = calendar.Time(config.get(section, "begin"))
                    event.end = calendar.Time(config.get(section, "end"))
                    event.course = courselist.getCourse(config.get(section, "course"))
                    event.type = config.get(section, "type")
                except ConfigParser.NoOptionError:
                    raise error.DataError(U_("Felaktig data i fil") + " " + filename)

                try:
                    event.group = config.getint(section, "group")
                except ConfigParser.NoOptionError:
                    event.group = 0
                    
                try:
                    event.seriesno = config.getint(section, "seriesno")
                except ConfigParser.NoOptionError:
                    event.seriesno = 0
                
                try:
                    if not config.getint(section, "active"):
                        event.active = False
                except ConfigParser.NoOptionError:
                    event.active = True

                self.addEvent(event)

    def save(self, filename = ""):
        "Sparar schemat till en INI-liknande fil"

        import configfileparser

        if not filename:
            import settings
            filename = settings.timetablefile

        config = configfileparser.ConfigParserX()

        if not self.isEmpty():
            config.add_section("main")
            config.set("main", "updated", str(self.updated))
            config.set("main", "username", self.username)

            for event in self.eventlist.getAll():
                config.add_section(event.getID())
                config.set(event.getID(), "date", str(event.date))
                config.set(event.getID(), "begin", str(event.begin))
                config.set(event.getID(), "end", str(event.end))
                config.set(event.getID(), "location", event.location)
                config.set(event.getID(), "course", event.course.code)
                config.set(event.getID(), "type", event.type)
                
                if event.group: config.set(event.getID(), "group", event.group)
                if event.seriesno: config.set(event.getID(), "seriesno", event.seriesno)
                if not event.active: config.set(event.getID(), "active", "0")
        
        global courselist
        if not courselist.isEmpty():
            config.add_section("courses")
            for course in courselist.courses:
                value = course.name + "|" + str(course.id) + "|" + str(course.group)
                config.set("courses", course.code, value)

        try:
            config.write(file(filename, "w+"))
        except IOError:
            raise error.WriteError(U_("Kan inte skriva till fil"), filename)
    
# -----------------------------------------------------------
class Course:
    "En kurs"
    
    def __init__(self, code, name, id = 0, group = 0):
        if not isinstance(code, unicode):
            code = unicode(code, "latin_1")
        if not isinstance(name, unicode):
            name = unicode(name, "latin_1")

        self.code = code
        self.name = name
        self.id = id
        self.group = group
    
    def __eq__(self, other):
        othercode = other
        if isinstance(other, Course):
            othercode = other.code
        
        if " " in self.code or " " in othercode:
            # Vissa kurser heter ex. "5B1506 IT" men exporteras bara som 5B1506
            return self.code.split(" ")[0] == othercode.split(" ")[0]
        elif len(self.code) >= 20 or len(othercode) >= 20:
            # Daisy exporterar endast de 20 första tecknen i kurskoden
            return self.code[:20] == othercode[:20]
        else:
            return self.code == othercode

    def __ne__(self, other):
        return False == self.__eq__(other)
   
    def __str__(self):
        print "Warning! STR is deprecated (timetable.py, class Course)"
        return unicode(self).encode("latin_1")

    def __unicode__(self):
        if self.name: return self.name
        else: return self.code
   
    def __repr__(self):
        return self.code + self.name + str(self.id) + str(self.group)
    
# -----------------------------------------------------------
class Event:
    "En schemalagd händelse"

    def __init__(self, idordict = None, date = None, begin = None, end = None, location = None, summary = None, active = True):
        """
            Tar emot strängrepresentationer för de fält som Daisy anger
            och gör om till bättre lämpade typer samt tolkar
            beskrivningsdatat till grupp, kurskod och händelsetyp.
        """
        
        self.__id = ""           # händelsens id, privat variabel då tolkningen beror på den
        self.date = None         # datum för händelse
        self.begin = None        # tid då händelse börjar
        self.end = None          # tid då händelse slutar
        self.location = None     # plats för händelsen
    
        self.course = None       # händelsens kurs
        self.type = ""           # händelsens typ (ex. föreläsning, lektion, laboration, seminarium etc)
        self.group = 0           # händelsens gruppnummer (vissa lektioner etc är indelade i grupper)
        self.seriesno = 0        # händelsetypens löpnummer (ex. (föreläsning) 7, (lektion) 3)
        
        self.parser = None
        self.active = active     # händelsen är aktiv, dvs. ej "borttagen"
        
        if not idordict:
            # om id är None (eller inte satt) sätts inte instansens värden här
            return

        if isinstance(idordict, dict):
            self.copyFromDict(idordict)
        else:
            self.setID(idordict)
            self.setParser(idordict)
            if summary and self.parser:
                self.parseSummary(summary)
    
            if location: self.location = location
            if date: self.date = calendar.Date(date)
            if begin: self.begin = calendar.Time(begin)
            if end: self.end = calendar.Time(end)
            
    def __repr__(self):
        "Returnerar en exakt beskrivning av aktuell händelse"
        return str(self.__id) + str(self.date) + str(self.begin) + str(self.end) +\
            str(self.location) + unicode(self.course) + str(self.type) + str(self.group) + str(self.seriesno)

    def __str__(self):
        print "Warning! STR is deprecated (timetable.py, class Event)"
        return unicode(self).encode("latin_1")

    def __unicode__(self):
        "Returnerar en beskrivning av aktuell händelse, ex. 'Kursnamn Ö7 grp 3 (401)'"

        description = self.getDescriptionWithoutLocation()
        if self.location: description += " (" + self.location + ")"
        return description

    def __eq__(self, other):
        if self.__id == other.__id and\
            self.date == other.date and\
            self.begin == other.begin and\
            self.end == other.end and\
            self.location == other.location and\
            self.type == other.type and\
            self.group == other.group and\
            self.seriesno == other.seriesno and\
            self.course == other.course: return True
        else:
            return False

    def __ne__(self, other):
        return False == self.__eq__(other)
    
    def getNiceString(self):
        string = "[" + self.begin.getNiceString() + "-" + self.end.getNiceString() + "] " + unicode(self)
        if not self.active:
            string = U_("inaktiverad")
        return string

    def setID(self, id):
        self.__id = id
        if id.endswith("timeedit.evolvera.se"):
            # även tidsstämpel för när schemat genererades inkluderas
            # i TimeEdits "id"
            try:
                self.__id = id.split("-")[1]
            except IndexError:
                pass
            
    def getID(self):
        return self.__id
            
    def setParser(self, id):
        self.parser = None
        if id.startswith("DAISYKTH"):
            self.parser = daisy.SummaryParser()
        elif id.endswith("timeedit.evolvera.se"):
            self.parser = timeedit.SummaryParser()

    def parseSummary(self, summary):
        global courselist
        if self.parser:
            data = self.parser.parse(summary)
            self.type = data["type"]
            self.location = data["location"]
            self.course = courselist.getCourse(data["course"])
            self.group = data["group"]
            self.seriesno = data["seriesno"]
        else:
            raise RuntimeError(U_("Ingen parser ar initialiserad"))
    
    def copyFromDict(self, other):
        keys = other.keys()
        if "id" in keys:
            self.setID(other["id"])
            self.setParser(other["id"])
        if "summary" in keys: self.parseSummary(other["summary"])
        if "date" in keys: self.date = calendar.Date(other["date"])
        if "begin" in keys: self.begin = calendar.Time(other["begin"])
        if "end" in keys: self.end = calendar.Time(other["end"])
        if "type" in keys: self.type = other["type"]
        if "group" in keys: self.group = other["group"]
        if "seriesno" in keys: self.seriesno = other["seriesno"]
        if "course" in keys: self.course = other["course"]
        if "active" in keys: self.active = other["active"]
        if "location" in keys and other["location"]:
            self.location = other["location"]
        
    def copy(self, other):
        self.__id = other.__id
        self.date = other.date
        self.begin = other.begin
        self.end = other.end
        self.location = other.location
        self.type = other.type
        self.group = other.group
        self.seriesno = other.seriesno
        self.course = other.course
        self.active = other.active

    def getDescriptionWithoutLocation(self):
        global courselist
        
        description = ""
        if self.course:
            try:
                description = courselist.getCourseName(self.course) + " "
            except ValueError:
                description = unicode(self.course) + " "

        if self.type == u"Föreläsning": description += U_("F")
        elif self.type == u"Övning": description += U_("O")
        elif self.type == u"Lektion": description += U_("Lekt")
        elif self.type == u"Seminarium": description += U_("Sem")
        elif self.type == u"Laboration": description += U_("Labb")
        elif self.type == u"Kontrollskrivning": description += U_("KS")
        elif self.type == u"Salsskrivning": description += U_("Tenta")
        elif self.type == u"Tentamen": description += U_("Tenta")
        elif self.type == u"Workshop": description += U_("WS")
        elif self.type == u"Introduktion": description += U_("Intro")
        elif self.type == u"Information": description += U_("Info")
        elif self.type == "": description += "???"
        else: description += self.type

        if self.seriesno: description += str(self.seriesno)
        if self.group: description += " " + U_("grp") + " " + str(self.group)

        return description
    
    def isGroupChosen(self):
        """
            Om händelsens grupp är 0 är den inte gruppindelad och ska visas.
            Om vald grupp är 0 ska alla grupper visas.
            Om vald grupp är lika med händelsens grupp ska den visas.
        """

        val = False
        if not self.group or not self.course.group or self.group == self.course.group:
            val = True
        return val
    
    def toggleActive(self):
        if self.active: self.active = False
        else: self.active = True

# -----------------------------------------------------------
class EventList:
    def __init__(self, list=None):
        self.events = {}
        if list:
            self.addEvents(list)
            
    def clear(self):
        self.events = {}
    
    def isEmpty(self):
        return self.events == {}
    
    def getAll(self):
        return self.events.values()
        
    def addEvent(self, event):
        if isinstance(event, Event):
            self.events[event.getID()] = event
        else:
            try:
                newevent = Event(event)
                self.events[newevent.getID()] = newevent
            except ValueError, e:
                # när en händelse skapas som inte hör till någon
                # känd kurs avbryts inte all inläsning utan just
                # den händelsen ignoreras
                import sys
                sys.stderr.write("\n" + str(e) + "\n")

    def addEvents(self, list):
        for event in list:
            self.addEvent(event)
            
    def removeEvent(self, id):
        try:
            del self.events[id]
        except KeyError:
            raise ValueError(U_("Handelsen") + " " + str(id) + " " + U_("finns inte"))
            
    def getEvent(self, id):
        try:
            return self.events[id]
        except KeyError:
            raise ValueError(U_("Handelsen") + " " + str(id) + " " + U_("finns inte"))

# -----------------------------------------------------------
class TimeTableComparator:
    
    def compare(self, timetable1, timetable2):
        pass

    def getDifference(self, events):
        return {"added": self.getAdded(events), "removed": self.getRemoved(events),
            "changed": self.getChanged(events)}

    def getAdded(self, events):
        added = []
        for event in events:
            try:
                self.getEvent(event.getID())
            except ValueError:
                added.append(event.getID())

        return added
        
    def getRemoved(self, events):
        removed = []
        for event in self.events:
            found = False
            
            for newevent in events:
                if event.getID() == newevent.getID():
                    found = True
                    break
            
            if not found:
                removed.append(event.getID())
        
        return removed

    def getChanged(self, events):
        changed = []
        for event in events:
            try:
                oldevent = self.getEvent(event.getID())
            except ValueError:
                continue
            
            if oldevent != event:
                changed.append(event.getID())

        return changed

# -----------------------------------------------------------
class VCalendarExporter:
    
    def export(self, filename, timetable, fromdate, todate):
        "Exporterar data till fil"
        events = timetable.getEventsForDateRange(fromdate, todate)
        activeevents = []
        for event in events:
            if event.active: activeevents.append(event)

        self.write(activeevents, filename)

    def write(self, events, filename):        
        import vcalendar
        vcalendar.Writer().write(events, filename)

# -----------------------------------------------------------
class HTMLExporter:

    def export(self, filename, timetable, fromdate, todate):
        self.timetable = timetable
        self.html = """<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.1//EN'
            'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd'>
            <html xmlns='http://www.w3.org/1999/xhtml' xml:lang='sv'>
            <head>
            <title>""" + U_("Schema") + """</title>
            <meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
            <meta name='generator' content='KTH TimeTable' />
            <link rel='stylesheet' type='text/css' href='timetable-html.css' />
            </head>
            <body><h1>""" + U_("Schema") + "</h1>"

        date = fromdate.getLastMonday()
        while date <= todate:
            self.formatWeek(date)
            date += 7
            
        self.html += "</body></html>"
        file(filename, "w+").write(self.html.encode("utf8"))

    def formatWeek(self, date):
        import settings
        self.html += "<div class='week'><h2>" + U_("Vecka") + " " + str(date.getWeek()) + "</h2>"
        for i in range(settings.lastweekday + 1):
            events = EventSorter().sort(self.timetable.getEventsForDate(date))
            self.formatDay(date, events)
            date += 1
            
        self.html += "</div>\n"

    def formatDay(self, date, events):
        self.html += "<div class='day'><h3>" + date.getWeekDayName() +\
            " " + str(date.getDay()) + "/" + str(date.getMonth()) + "</h3>"
        for event in events:
            self.formatEvent(event)

        self.html += "</div>"

    def formatEvent(self, event):
        if event.active:
            self.html += "<div class='event'>" +\
                event.begin.getNiceString() + "-" + event.end.getNiceString() + ": " + unicode(event) +\
                "</div>"

# -----------------------------------------------------------
class CSVExporter(VCalendarExporter):
    "Exporterar schema till komma-separerad lista för ex. JPilot"
    
    def write(self, events, filename):
        data = """CSV datebook: Category, Private, Description, Note, Event, Begin, End, Alarm, Advance, Advance Units, Repeat Type, Repeat Forever, Repeat End, Repeat Frequency, Repeat Day, Repeat Days, Week Start, Number of Exceptions, Exceptions\n"""

        for event in events:
            data += self.formatEvent(event) + "\n"

        file(filename, "w+").write(data.encode("latin_1"))

    def formatEvent(self, event):
        import settings
        data = self.makeListItem(settings.event_export_category)
        data += self.makeListItem("0")
        data += self.makeListItem(unicode(event))
        data += self.makeListItem("")
        data += self.makeListItem("0")
        data += self.makeListItem(self.formatDateAndTime(event.date, event.begin))
        data += self.makeListItem(self.formatDateAndTime(event.date, event.end))
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        data += self.makeListItem("1")
        data += self.makeListItem("0")
        data += self.makeListItem("0")
        return data[:-1]

    def formatDateAndTime(self, date, time):
        return str(date.getYear()) + " " + str(date.getMonth()) + " " + str(date.getDay()) +\
            "  " + time.getNiceString()

    def makeListItem(self, item):
        return "\"" + item + "\","

# -----------------------------------------------------------
class EventSorter:
    
    def helper(self, event1, event2):
        if event1.date < event2.date:
            return -1
        if event1.date > event2.date:
            return 1
        if event1.begin < event2.begin:
            return -1
        if event1.begin > event2.begin:
            return 1
        
        return 0
    
    def sort(self, events):
        events.sort(self.helper)
        return events        

# -----------------------------------------------------------
courselist = CourseList()
timetable = TimeTable()
timetable.load()
