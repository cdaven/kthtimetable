# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import calendar
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
    
    def addCourse(self, codeorcourse, name = "", id = 0, group = ""):
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

    def hasCourse(self, course):
        for c in self.courses:
            if c == course: return True
        return False

    def getCourse(self, code):
        "Returnerar en kurs definierad av kod"

        for course in self.courses:
            if course == code: return course

        raise ValueError(U_("The course") + " " + U_("does not exist") + " (" + U_("code") + " " + str(code) + ")")

    def getCourseName(self, code):
        "Returnerar namnet (ev. användardefinierat) på en kurs"
        return self.getCourse(code).name

    def setCourseName(self, code, name):
        self.getCourse(code).name = name

    def getCourseGroup(self, code):
        "Returnerar vald grupp för aktuell kurs"
        return self.getCourse(code).group

    def setCourseGroup(self, code, group):
        self.getCourse(code).group = group

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
            if course.isDaisy(): codes.append(course.code)

        return codes

    def getAllTimeEditCourseCodes(self):
        codes = []
        for course in self.courses:
            if course.isTimeEdit(): codes.append(course.code)

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

    def getAllPersistentCourses(self):
        courses = []
        courses += self.getAllTimeEditCourses()
        courses += self.getAllDaisyCourses()
        return courses

    def getAllCourses(self):
        courses = []
        for course in self.courses:
            courses.append(course)

        return courses

    def getAllMatchingName(self, name):
        courses = []

        for course in self.courses:
            # Daisy exporterar ibland ofullständigt namn
            if course.name.startswith(name):
                courses.append(course)

        return courses

    def pickle(self):
        import StringIO
        import pickle
        string = StringIO.StringIO()
        pickle.dump(self.getAllPersistentCourses(), string)
        return string.getvalue()

    def unpickle(self, data):
        import StringIO
        import pickle
        string = StringIO.StringIO(data)
        self.courses = pickle.load(string)

# -----------------------------------------------------------
class CachedCourseList(CourseList):
    "Lista med kurser som hämtats från ITU:s webbplats"

    filename = "daisycourses"

    def __init__(self):
        import os.path
        import time

        try:
            self.unpickle(file(self.filename).read())
            if self.isOldList(calendar.Date(time.localtime(os.path.getctime(self.filename)))):
                self.courses = []
            else:
                # omvandlar gamla heltalsgrupper till strängar
                # bör tas bort till version 2.4
                courses = []
                for course in self.courses:
                    if isinstance(course.group, int):
                        course.group = str(course.group)
                        if course.group == "0": course.group = ""
                    courses.append(course)
                self.courses = courses
        except IOError:
            self.courses = []

    def isEmpty(self):
        return self.courses == []

    def isOldList(self, date):
        diff = calendar.Date() - date
        monthtoday = calendar.Date().getMonth()
        monththen = date.getMonth()

        if (monthtoday > 9 and monththen < 10) or diff > 90:
            return True
        elif (monthtoday > 2 and monththen < 3) or diff > 90:
            return True

        return False

    def save(self):
        file(self.filename, "w+").write(self.pickle())

    def setCourses(self, courselist):
        self.courses = courselist

    def getCourses(self, code):
        courses = []
        code = code.upper()
        for course in self.courses:
            if self.isMatch(code, course):
                courses.append(course)

        return courses

    def isMatch(self, code, course):
        codes = course.code.split("/")
        for c in codes:
            if code in c:
                return True

        return False


# -----------------------------------------------------------
class TimeTable:
    "Ett schema (dvs en samling schemalagda händelser)"

    def __init__(self):
        self.eventlist = EventList()
        self.updated = None
        self.courselist = CourseList()
        
    def clear(self):
        self.eventlist.clear()
        self.updated = None
        
    def addEvent(self, event):
        self.eventlist.addEvent(event)

    def getAllEvents(self):
        return self.eventlist.getAll()

    def getAllDaisyEvents(self):
        return self.eventlist.getAllDaisyEvents()
        
    def getAllTimeEditEvents(self):
        return self.eventlist.getAllTimeEditEvents()
    
    def getAllPersistentCourses(self):
        return self.courselist.getAllPersistentCourses()

    def isEmpty(self):
        return self.eventlist.isEmpty()

    def importVCalData(self, input, course = None):
        """
            Importerar aktiviteter från vCalendar-formatet.
            Anges "course" kommer alla aktiviteter tillhöra
            denna kurs.
        """

        import vcalendar
        events = vcalendar.Reader().read(input)
        if events:
            # tar också bort de händelser som inte längre
            # finns på servern, mha EventCleaner
            cleaner = EventCleaner()
            cleaner.reset()
            self.eventlist.addEvents(events, course)
            cleaner.sweep(self)
            self.updated = calendar.Date()

    def getEvent(self, id):
        return self.eventlist.getEvent(id)

    def getAllGroups(self, code):
        "Returnerar alla möjliga grupper för en viss kurs"

        groups = []
        events = self.getAllEventsForCourse(code)
        for event in events:
            if event.group and event.group not in groups:
                groups.append(event.group)

        return groups

    def getAllEventsForCourse(self, code):
        return self.eventlist.getAllEventsForCourse(code)

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
        self.eventlist.removeCourseEvents(course)

    def removeEvent(self, id):
        self.eventlist.removeEvent(id)

    def removeOrphanEvents(self):
        "Tar bort alla händelser vars kurs inte längre finns i kurslistan"

        global courselist
        remove = []

        for event in self.eventlist.getAll():
            if not courselist.hasCourse(event.course):
                self.eventlist.removeEvent(event.getID())

    def load(self, filename = ""):
        "Läser in schemat från en INI-liknande fil"

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
            raise error.ReadError(U_("Could not read from"), filename)

        # läser först in inställningarna och kurserna ...
        for section in config.sections():
            if section == "main":
                self.updated = calendar.Date(config.get(section, "updated"))

            elif section == "courses":
                pairs = config.items(section)
                for pair in pairs:
                    code = pair[0]
                    data = pair[1].split("|")
                    courselist.addCourse(code, data[0], int(data[1]), data[2])

        # ... och därefter alla händelser som beror på de inlästa kurserna
        for section in config.sections():
            if section != "main" and section != "courses" and section != "settings":
                event = Event()

                event.setID(section)
                event.location = config.get(section, "location")
                event.date = calendar.Date(config.get(section, "date"))
                event.begin = calendar.Time(config.get(section, "begin"))
                event.end = calendar.Time(config.get(section, "end"))
                event.course = courselist.getCourse(config.get(section, "course"))
                event.type = config.get(section, "type")

                event.group = config.getstrorempty(section, "group")
                event.seriesno = config.getintorzero(section, "seriesno")
                event.active = config.getboolean(section, "active")

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

            for event in self.eventlist.getAllPersistent():
                config.add_section(event.getID())
                config.set(event.getID(), "date", str(event.date))
                config.set(event.getID(), "begin", str(event.begin))
                config.set(event.getID(), "end", str(event.end))
                config.set(event.getID(), "location", event.location)
                config.set(event.getID(), "course", event.course.code)
                config.set(event.getID(), "type", event.type)
                
                if event.group: config.set(event.getID(), "group", event.group)
                if event.seriesno: config.set(event.getID(), "seriesno", event.seriesno)
                if not event.active: config.set(event.getID(), "active", "false")
        
        global courselist
        if not courselist.isEmpty():
            config.add_section("courses")
            for course in courselist.getAllPersistentCourses():
                value = course.name + "|" + str(course.id) + "|" + course.group
                config.set("courses", course.code, value)

        try:
            config.write(file(filename, "w+"))
        except IOError:
            raise error.WriteError(U_("Could not write to"), filename)
    
# -----------------------------------------------------------
class Course:
    "En kurs"
    
    def __init__(self, code, name, id = 0, group = ""):
        if not isinstance(code, unicode):
            code = unicode(code, "latin_1")
        if not isinstance(name, unicode):
            name = unicode(name, "latin_1")

        self.code = code
        self.name = name
        self.id = id

        group = str(group)
        if group == "0": group = ""
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
        return unicode(self).encode("latin_1")

    def __unicode__(self):
        if self.name: return self.name
        else: return self.code
   
    def __repr__(self):
        return self.code + self.name + str(self.id) + self.group

    def isDaisy(self):
        val = False
        if self.id: val = True
        return val
    
    def isTimeEdit(self):
        return False == self.isDaisy()


# -----------------------------------------------------------
class SubscribedCourse(Course):
    "En 'kurs' för prenumererade aktiviteter"

    def __init__(self, code):
        Course.__init__(self, code, code)

    def __unicode__(self):
        return unicode(self.code, "latin_1")

    def isTimeEdit(self):
        return False


# -----------------------------------------------------------
class Event:
    "En schemalagd händelse"

    def __init__(self, data = None):
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
        self.group = ""          # händelsens gruppnummer (vissa lektioner etc är indelade i grupper)
        self.seriesno = 0        # händelsetypens löpnummer (ex. (föreläsning) 7, (lektion) 3)
        
        self.parser = None
        self.active = True       # händelsen är aktiv, dvs. ej "borttagen"

        self.flag = None         # används för att se om en händelse inte har uppdaterats
                                 # vid synkronisering, dvs. om den egentligen är borttagen
        
        if not data:
            # om data är None sätts inte instansens värden här
            return
        else:
            self.copyFromDict(data)
            
    def __repr__(self):
        "Returnerar en exakt beskrivning av aktuell händelse"
        return str(self.__id) + str(self.date) + str(self.begin) + str(self.end) +\
            str(self.location) + unicode(self.course) + str(self.type) + self.group + str(self.seriesno)

    def __str__(self):
        return unicode(self).encode("latin_1")

    def __unicode__(self):
        "Returnerar en beskrivning av aktuell händelse, ex. 'Kursnamn Ö7 grp 3 (401)'"

        description = self.getDescriptionWithoutLocation()
        if self.location: description += " (" + self._manipulateLocation(self.location) + ")"
        return description

    def __eq__(self, other):
        if self.getID() == other.getID() and\
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

    def copyDetails(self, other):
        "Kopierar tid, plats och datum från annan aktivitet"

        self.begin = other.begin
        self.end = other.end
        self.location = other.location
        self.date = other.date
    
    def getNiceString(self):
        string = "[" + self.begin.getNiceString() + "-" + self.end.getNiceString() + "] " + unicode(self)
        if not self.active:
            string = U_("inactivated")
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
            import daisy
            self.parser = daisy.SummaryParser()
        elif id.endswith("timeedit.evolvera.se"):
            import timeedit
            self.parser = timeedit.SummaryParser()

    def _parseSummary(self, summary):
        global courselist
        data = self.parser.parse(summary)
        self.type = data["type"]
        self.group = data["group"]
        self.seriesno = data["seriesno"]
        if not self.location:
            # om inte copyFromDict redan satt lokalen,
            # som den gör för Daisy-aktiviteter
            self.location = data["location"]

        try:
            if not self.course:
                # om inte copyFromDict redan satt kursen,
                # som den gör om kursen anges explicit
                self.course = courselist.getCourse(data["course"])
        except ValueError:
            "Testar alternativa sätt att hitta rätt kurs för aktivitet"

            if self.__id.startswith("DAISYKTH"):
                course = self._findDaisyCourse(data["course"])
                if course: self.course = course
                else: raise
            elif self.__id.endswith("timeedit.evolvera.se"):
                course = self._findTimeEditCourse(data["course"])
                if course: self.course = course
                else: raise

    def _findDaisyCourse(self, name):
        """
            Hittar en Daisy-kurs via dess ursprungliga namn;
            om flera kurser har samma namn hämtas den (om någon)
            som redan finns i kurslistan.
        """

        global courselist
        stored = CachedCourseList().getAllMatchingName(name)
        course = None

        for course in stored:
            try:
                course = courselist.getCourse(course.code)
                break
            except ValueError:
                pass

        return course

    def _findTimeEditCourse(self, courses):
        "Hittar en TimeEdit-kurs genom att prova alla i en lista"

        global courselist
        courses = courses.split(",")
        course = None
        for c in courses:
            try:
                course = courselist.getCourse(c)
                break
            except ValueError:
                pass

        return course

    def copyFromDict(self, other):
        keys = other.keys()
        if "id" in keys:
            self.setID(other["id"])
            self.setParser(other["id"])
        if "course" in keys: self.course = other["course"]
        if "date" in keys: self.date = calendar.Date(other["date"])
        if "begin" in keys: self.begin = calendar.Time(other["begin"])
        if "end" in keys: self.end = calendar.Time(other["end"])
        if "type" in keys: self.type = other["type"]
        if "group" in keys: self.group = other["group"]
        if "seriesno" in keys: self.seriesno = other["seriesno"]
        if "active" in keys: self.active = other["active"]
        if "location" in keys: self.location = other["location"]
        if "summary" in keys and self.parser: self._parseSummary(other["summary"])

    def _manipulateLocation(self, location):
        """
            Tar bort Daisy-prefixen Hörsal och Övningssal för
            kurser på Valhallavägen samt möjliggör översättning
            av språkspecifika ord som Sal, Aulan etc.
        """

        location = location.replace(u"Övningssal ", "")
        location = location.replace(u"Hörsal ", "")
        location = location.replace(u"Sal", U_("Room"))
        location = location.replace(u"Aulan", U_("Great Hall"))
        return location

    def getDescriptionWithoutLocation(self):
        global courselist
        
        description = ""
        if self.course:
            try:
                description = courselist.getCourseName(self.course) + " "
            except ValueError:
                description = unicode(self.course) + " "

        if self.type == u"Föreläsning": description += U_("Lect")
        elif self.type == u"Övning": description += U_("Tut")
        elif self.type == u"Lektion": description += U_("Lesson")
        elif self.type == u"Seminarium": description += U_("Sem")
        elif self.type == u"Laboration": description += U_("Lab")
        elif self.type == u"Kontrollskrivning": description += U_("Quiz")
        elif self.type == u"Salsskrivning": description += U_("Exam")
        elif self.type == u"Tentamen": description += U_("Exam")
        elif self.type == u"Workshop": description += U_("WS")
        elif self.type == u"Introduktion": description += U_("Intro")
        elif self.type == u"Information": description += U_("Info")
        elif self.type == "": description += "???"
        else: description += self.type

        if self.seriesno: description += str(self.seriesno)
        if self.group: description += " " + U_("grp") + " " + self.group

        return description
    
    def isGroupChosen(self):
        """
            Om händelsens grupp är tom är den inte gruppindelad och ska visas.
            Om vald grupp är tom ska alla grupper visas.
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
class SubscribedEvent(Event):
    """
        En aktivitet som inte kommer direkt från Daisy eller TimeEdit
        utan är importerad/prenumererad från annan källa.
    """

    def __init__(self, data):
        Event.__init__(self)

        self.__id = data["id"]
        self.course = data["course"]
        self.date = calendar.Date(data["date"])
        self.begin = calendar.Time(data["begin"])
        self.end = calendar.Time(data["end"])
        self.type = u"Föreläsning"
        self.user = data["user"]

    def __unicode__(self):
        return unicode(self.user, "latin_1")

    def copyDetails(self, other):
        pass

    def getID(self):
        return self.__id

    def isGroupChosen(self):
        return True

    def toggleActive(self):
        pass


# -----------------------------------------------------------
class EventList:
    def __init__(self, list = None):
        self.events = {}
        if list:
            self.addEvents(list)
            
    def clear(self):
        self.events = {}
    
    def isEmpty(self):
        return self.events == {}
    
    def getAll(self):
        return self.events.values()

    def getAllPersistent(self):
        """
            Returnerar alla aktiviteter som hör till det
            aktuella schemat; dvs. som inte är "prenumererade"
        """

        events = []
        for event in self.getAll():
            if not isinstance(event, SubscribedEvent):
                events.append(event)

        return events

    def getAllDaisyEvents(self):
        events = []
        for event in self.events:
            if event.course.isDaisy(): events.append(event)
        
        return events
        
    def getAllTimeEditEvents(self):
        events = []
        for event in self.events:
            if event.course.isTimeEdit(): events.append(event)
        
        return events

    def getAllEventsForCourse(self, code):
        "Returnerar alla händelser för en viss kurs, utan hänsyn till gruppval"
        
        events = []
        coursefound = False
        for event in self.getAll():
            if event.course == code:
                coursefound = True
                events.append(event)

        if not coursefound:
            raise ValueError(U_("The course") + " " + str(code) + " " + U_("does not exist"))
            
        return events

    def removeCourseEvents(self, course):
        "Tar bort alla händelser för en viss kurs"

        try:
            remove = self.getAllEventsForCourse(course)
            for event in remove:
                self.removeEvent(event.getID())
        except ValueError:
            return # redan borttaget

    def hasEvent(self, id):
        return id in self.events.keys()

    def _add(self, event):
        """
            Lägger till en aktivitet. ID är en unik nyckel i listan.
            Nya aktiviteter med ID som redan existerar skriver
            _inte_ över existerande aktiviteter.
        """

        if self.hasEvent(event.getID()):
            # kopierar tid, plats och datum från ny aktivitet
            # till existerande
            self.getEvent(event.getID()).copyDetails(event)
        else:
            # aktiviteten är ny, lägg bara till
            self.events[event.getID()] = event

        EventCleaner().mark(self.getEvent(event.getID()))

    def addEvent(self, event, course = None):
        if isinstance(event, Event):
            self._add(event)
        else:
            # sätter i förekommande fall kursen explicit
            if course: event["course"] = course

            try:
                self._add(Event(event))
            except ValueError, e:
                # när en händelse skapas som inte hör till någon
                # känd kurs avbryts inte all inläsning utan just
                # den händelsen ignoreras
                import sys
                sys.stderr.write("\n" + str(e) + "\n")

    def addEvents(self, list, course = None):
        for event in list:
            self.addEvent(event, course)
            
    def removeEvent(self, id):
        try:
            del self.events[id]
        except KeyError:
            raise ValueError(U_("The event") + " " + str(id) + " " + U_("does not exist"))
            
    def getEvent(self, id):
        try:
            return self.events[id]
        except KeyError:
            raise ValueError(U_("The event") + " " + str(id) + " " + U_("does not exist"))


# -----------------------------------------------------------
class EventCleaner:
    """
        Rensar borttagna händelser enligt Mark-Sweep-algoritmen.

        Varje uppdaterad händelse som hämtats från schemaservern
        markeras. De som sedan inte markerats tas bort.
    """

    __shared_state = {}
    okflag = False

    def __init__(self):
        self.__dict__ = self.__shared_state

    def reset(self):
        self.okflag = not self.okflag

    def mark(self, event):
        event.flag = self.okflag

    def sweep(self, timetable):
        for event in timetable.getAllEvents():
            if not event.flag == self.okflag:
                timetable.removeEvent(event.getID())


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
    
    def __init__(self, encoding = "latin_1"):
        self.encoding = encoding

    def export(self, filename, timetable, fromdate, todate):
        "Exporterar data till fil"
        events = timetable.getEventsForDateRange(fromdate, todate)
        activeevents = []
        for event in events:
            if event.active: activeevents.append(event)

        self.write(activeevents, filename)

    def write(self, events, filename):        
        import vcalendar
        vcalendar.Writer(self.encoding).write(events, filename)

# -----------------------------------------------------------
class HTMLExporter:

    def export(self, filename, timetable, fromdate, todate):
        self.timetable = timetable
        self.html = """<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.1//EN'
            'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd'>
            <html xmlns='http://www.w3.org/1999/xhtml' xml:lang='sv'>
            <head>
            <title>""" + U_("TimeTable") + """</title>
            <meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
            <meta name='generator' content='KTH TimeTable' />
            <link rel='stylesheet' type='text/css' href='timetable-html.css' />
            </head>
            <body><h1>""" + U_("TimeTable") + "</h1>"

        date = fromdate.getLastMonday()
        while date <= todate:
            self.formatWeek(date)
            date += 7
            
        self.html += "</body></html>"
        file(filename, "w+").write(self.html.encode("utf8"))

    def formatWeek(self, date):
        import settings
        self.html += "<div class='week'><h2>" + U_("Week") + " " + str(date.getWeek()) + "</h2>"
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

        file(filename, "w+").write(data.encode("utf8"))

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
