# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

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
        for course in self.getAllDaisyCourseIDs():
            self.removeCourse(course)
        
    def clearTimeEditCourses(self):
        for course in self.getAllTimeEditCourseIDs():
            self.removeCourse(course)

    def isEmpty(self):
        return self.courses == []
    
    def addCourse(self, idorcourse, name = "", id = "", group = ""):
        """
            L�gger till en kurs eller skriver �ver befintlig om samma id

            Det kan allts� finnas flera kurser med samma kod,
            men inte med samma kurs/moment-id.
        """

        if isinstance(idorcourse, Course):
            if self.hasCourse(idorcourse):
                self.courses.remove(idorcourse)
            self.courses.append(idorcourse)
        else:
            if self.hasCourse(idorcourse):
                self.courses.remove(self.getCourse(idorcourse))
            self.courses.append(Course(idorcourse, name, id, group))
        
    def removeCourse(self, id):
        "Tar bort en kurs ur listan"
        self.courses.remove(self.getCourse(id))

    def hasCourse(self, course):
        for c in self.courses:
            if c == course: return True
        return False

    def getCourse(self, id):
        "Returnerar en kurs definierad av id (kurskod eller Daisy-id)"
        for course in self.courses:
            if course == id: return course

        raise ValueError(U_("The course") + " " + U_("does not exist") + " (" + U_("code") + " " + str(id) + ")")

    def getCourseByCode(self, code):
        "Returnerar en kurs definierad av kurskod"
        for course in self.courses:
            if course.hasCode(code): return course

        raise ValueError(U_("The course") + " " + U_("does not exist") + " (" + U_("code") + " " + str(id) + ")")

    def getCourseName(self, code):
        "Returnerar namnet (ev. anv�ndardefinierat) p� en kurs"
        return self.getCourse(code).name

    def setCourseName(self, code, name):
        self.getCourse(code).name = name

    def getCourseGroup(self, code):
        "Returnerar vald grupp f�r aktuell kurs"
        return self.getCourse(code).group

    def setCourseGroup(self, code, group):
        self.getCourse(code).group = group

    def getCourseID(self, code):
        "Returnerar kurs-id p� en kurs"
        return self.getCourse(code).id

    def setCourseID(self, code, id):
        self.getCourse(code).id = id

    def getAllDaisyCourses(self):
        courses = []
        map(courses.append, map(self.getCourse, self.getAllDaisyCourseIDs()))
        return courses

    def getAllTimeEditCourses(self):
        courses = []
        map(courses.append, map(self.getCourse, self.getAllTimeEditCourseIDs()))
        return courses

    def getAllDaisyCourseIDs(self):
        ids = []
        for course in self.courses:
            if course.isDaisy(): ids.append(course.id)
        return ids

    def getAllTimeEditCourseIDs(self):
        ids = []
        for course in self.courses:
            if course.isTimeEdit(): ids.append(course.id)
        return ids

    def getAllPersistent(self):
        courses = []
        courses += self.getAllTimeEditCourses()
        courses += self.getAllDaisyCourses()
        return courses

    def getAllMatchingName(self, name):
        courses = []
        for course in self.courses:
            # Daisy exporterar ibland ofullst�ndigt namn
            if course.name.startswith(name):
                courses.append(course)
        return courses

    def getAllMatchingCode(self, code):
        courses = []
        code = code.upper()
        for course in self.courses:
            if code in course.code:
                courses.append(course)

        return courses

    def pickle(self):
        import StringIO
        import pickle
        string = StringIO.StringIO()
        pickle.dump(self.getAllPersistent(), string)
        return string.getvalue()

    def unpickle(self, data):
        import StringIO
        import pickle
        string = StringIO.StringIO(data)
        self.courses = pickle.load(string)


# -----------------------------------------------------------
class CachedCourseList(CourseList):
    "Lista med kurser som h�mtats fr�n ITU:s webbplats"

    filename = "daisycourses"

    def __init__(self):
        CourseList.__init__(self)
        self.courses = []
        self.readFromFile()

    def readFromFile(self):
        import os.path
        import time

        try:
            self.unpickle(file(self.filename).read())
            if self.isOldList(calendar.Date(time.localtime(os.path.getctime(self.filename)))):
                self.courses = []
            else:
                # omvandlar gamla heltalsgrupper till str�ngar
                # b�r tas bort till version 2.4
                courses = []
                for course in self.courses:
                    if isinstance(course.group, int):
                        course.group = str(course.group)
                        if course.group == "0": course.group = ""
                    courses.append(course)
                self.courses = courses
        except (IOError, EOFError):
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

# -----------------------------------------------------------
class TimeTable:
    "Ett schema (dvs en samling schemalagda h�ndelser)"

    def __init__(self):
        self.eventlist = EventList(self)
        self.courselist = CourseList()
        self.groups = {}
        self.updated = None
        
    def clear(self):
        self.eventlist.clear()
        self.courselist.clear()
        self.updated = None
        
    def importOneCourse(self, input, course):
        "Importerar h�ndelser f�r EN kurs fr�n vCalendar-data."

        import vcalendar
        events = vcalendar.Reader().read(input)
        if events:
            self.eventlist.addEvents(events, course)

    def importCourses(self, input):
        "Importerar h�ndelser fr�n vCalendar-data."

        import vcalendar
        events = vcalendar.Reader().read(input)
        if events:
            # tar ocks� bort de h�ndelser som inte l�ngre
            # finns p� servern, mha EventCleaner.
            cleaner = EventCleaner()
            cleaner.reset()

            self.eventlist.addEvents(events)

            cleaner.sweep(self)
            self.updated = calendar.Date()

    def getAllChosenEvents(self):
        events = []
        for event in self.eventlist.getAll():
            if event.isGroupChosen():
                events.append(event)

        return events

    def getAllGroups(self, code):
        "Returnerar alla m�jliga grupper f�r en viss kurs"

        groups = []
        events = self.getAllEventsForCourse(code)
        for event in events:
            if event.group and event.group not in groups:
                groups.append(event.group)

        return groups

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

    def removeOrphanEvents(self):
        "Tar bort alla h�ndelser vars kurs inte l�ngre finns i kurslistan"

        remove = []
        for event in self.eventlist.getAll():
            if not self.hasCourse(event.course):
                self.removeEvent(event.getID())

    def addSubscriptionGroup(self, name, members):
        if not isinstance(name, unicode):
            name = unicode(name, "latin_1")

        if isinstance(members, str):
            members = members.split("|")
        self.groups[name] = subscription.Group(name, members)

    def getAllSubscriptionGroupNames(self):
        names = self.groups.keys()
        names.sort()
        return names

    def getSubscriptionGroup(self, name):
        return self.groups[name]

    def removeSubscriptionGroup(self, name):
        try:
            del self.groups[name]
        except KeyError:
            pass

    def load(self, filename = ""):
        "L�ser in schemat fr�n en INI-liknande fil"

        import configfileparser
        import settings
        import os.path

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

        # l�ser f�rst in inst�llningarna och kurserna ...
        for section in config.sections():
            if section == "main":
                self.updated = calendar.Date(config.get(section, "updated"))

            elif section == "courses":
                pairs = config.items(section)
                for pair in pairs:
                    code = pair[0]
                    data = pair[1].split("|")
                    self.addCourse(code, name=data[0], id=data[1], group=data[2])

            elif section == "groups":
                pairs = config.items(section)
                for pair in pairs:
                    name = pair[0]
                    members = pair[1].split("|")
                    self.addSubscriptionGroup(name, members)

        # ... och d�refter alla h�ndelser som beror p� de inl�sta kurserna
        for section in config.sections():
            if section != "main" and section != "courses" and section != "settings" and section != "groups":
                event = Event(self)

                event.setID(section)
                event.location = config.get(section, "location")
                event.date = calendar.Date(config.get(section, "date"))
                event.begin = calendar.Time(config.get(section, "begin"))
                event.end = calendar.Time(config.get(section, "end"))
                event.course = self.getCourseByCode(config.get(section, "course"))
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
        
        if self.hasCourses():
            config.add_section("courses")
            for course in self.getAllPersistentCourses():
                value = course.name + "|" + str(course.id) + "|" + course.group
                config.set("courses", course.code, value)

        if self.groups:
            config.add_section("groups")
            for name in self.getAllSubscriptionGroupNames():
                config.set("groups", name, str(self.getSubscriptionGroup(name)))

        try:
            config.write(file(filename, "w+"))
        except IOError:
            raise error.WriteError(U_("Could not write to"), filename)

    # -- delegeringar till EventList

    def isEmpty(self):
        return self.eventlist.isEmpty()

    def addEvent(self, event):
        self.eventlist.addEvent(event)

    def getAllEvents(self):
        return self.eventlist.getAll()

    def getAllDaisyEvents(self):
        return self.eventlist.getAllDaisyEvents()
        
    def getAllTimeEditEvents(self):
        return self.eventlist.getAllTimeEditEvents()

    def getEvent(self, id):
        return self.eventlist.getEvent(id)

    def getAllEventsForCourse(self, code):
        return self.eventlist.getAllEventsForCourse(code)

    def removeCourseEvents(self, course):
        self.eventlist.removeCourseEvents(course)

    def removeEvent(self, id):
        self.eventlist.removeEvent(id)

    # -- delegeringar till CourseList

    def hasCourses(self):
        return not self.courselist.isEmpty()

    def clearCourses(self):
        self.courselist.clear()

    def clearDaisyCourses(self):
        self.courselist.clearDaisyCourses()
        
    def clearTimeEditCourses(self):
        self.courselist.clearTimeEditCourses()

    def addCourse(self, codeorcourse, name = "", id = 0, group = ""):
        self.courselist.addCourse(codeorcourse, name, id, group)
        
    def removeCourse(self, code):
        self.courselist.removeCourse(code)

    def hasCourse(self, course):
        return self.courselist.hasCourse(course)

    def getCourse(self, code):
        return self.courselist.getCourse(code)

    def getCourseByCode(self, code):
        return self.courselist.getCourseByCode(code)

    def getCourseName(self, code):
        return self.courselist.getCourseName(code)

    def setCourseName(self, code, name):
        self.courselist.setCourseName(code, name)

    def getCourseGroup(self, code):
        return self.courselist.getCourseGroup(code)

    def setCourseGroup(self, code, group):
        self.courselist.setCourseGroup(code, group)

    def getCourseID(self, code):
        return self.courselist.getCourseID(code)

    def setCourseID(self, code, id):
        self.courselist.setCourseID(code, id)

    def getAllDaisyCourses(self):
        return self.courselist.getAllDaisyCourses()

    def getAllTimeEditCourses(self):
        return self.courselist.getAllTimeEditCourses()

    def getAllDaisyCourseIDs(self):
        return self.courselist.getAllDaisyCourseIDs()

    def getAllTimeEditCourseIDs(self):
        return self.courselist.getAllTimeEditCourseIDs()

    def getAllPersistentCourses(self):
        return self.courselist.getAllPersistent()

    def getAllCoursesMatchingName(self, name):
        return self.courselist.getAllMatchingName(name)

    def pickleCourses(self):
        return self.courselist.pickle()

    def unpickleCourses(self, data):
        self.courselist.unpickle(data)

# -----------------------------------------------------------
class Course:
    "En kurs"
    
    def __init__(self, code, name, id = "", group = "", term = ""):
        if not isinstance(code, unicode):
            code = unicode(code, "latin_1")
        if not isinstance(name, unicode):
            name = unicode(name, "latin_1")

        self.code = code    # kurskod
        self.name = name    # kursnamn eller beteckning
        self.id = id        # Daisys kurs-id eller TimeEdits kurskod
        if not id:
            self.id = code
        self.term = term    # starttermin f�r kursen (endast Daisy)

        group = str(group)
        if group == "0": group = ""
        self.group = group

    def __eq__(self, other):
        "J�mf�r kurskod f�r TimeEdit-kurser (=id) eller Daisy-id"
        if isinstance(other, Course):
            other = other.id
        return self.id == other

    def hasCode(self, code):
        if " " in self.code or " " in code:
            # Vissa kurser i Daisy heter ex. "5B1506 IT"
            # men exporteras bara som 5B1506
            return self.code.split(" ")[0] == code.split(" ")[0]
        elif len(self.code) >= 20 or len(code) >= 20:
            # Daisy exporterar endast de 20 f�rsta tecknen i kurskoden
            return self.code[:20] == code[:20]
        else:
            return self.code == code

    def __ne__(self, other):
        return not self == other
   
    def __str__(self):
        return unicode(self).encode("latin_1")

    def __unicode__(self):
        if self.name: return self.name
        else: return self.code
   
    def __repr__(self):
        return self.code + self.name + str(self.id) + self.group

    def isDaisy(self):
        return not self.isTimeEdit()
    
    def isTimeEdit(self):
        val = False
        if self.code == self.id: val = True
        return val

    def getTerm(self):
        "Returnerar terminen f�r kursen, ex. 'VT05'"
        if self.term == "": return "?"
        term = "HT"
        if self.term[-1] == "1": term = "VT"
        return term + self.term[2:4]


# -----------------------------------------------------------
class Event:
    "En schemalagd h�ndelse"

    cachedcourselist = CachedCourseList() # beh�vs f�r att kolla upp Daisy-kurser

    def __init__(self, timetable, data = None):
        """
            Tar emot str�ngrepresentationer f�r de f�lt som Daisy anger
            och g�r om till b�ttre l�mpade typer samt tolkar
            beskrivningsdatat till grupp, kurskod och h�ndelsetyp.
        """
        
        self.__id = ""           # h�ndelsens id, privat variabel d� tolkningen beror p� den
        self.date = None         # datum f�r h�ndelse
        self.begin = None        # tid d� h�ndelse b�rjar
        self.end = None          # tid d� h�ndelse slutar
        self.location = None     # plats f�r h�ndelsen
    
        self.course = None       # h�ndelsens kurs
        self.type = ""           # h�ndelsens typ (ex. f�rel�sning, lektion, laboration, seminarium etc)
        self.group = ""          # h�ndelsens gruppnummer (vissa lektioner etc �r indelade i grupper)
        self.seriesno = 0        # h�ndelsetypens l�pnummer (ex. (f�rel�sning) 7, (lektion) 3)
        
        self.parser = None
        self.active = True       # h�ndelsen �r aktiv, dvs. ej "borttagen"

        self.flag = None         # anv�nds f�r att se om en h�ndelse inte har uppdaterats
                                 # vid synkronisering, dvs. om den egentligen �r borttagen

        self.timetable = timetable
        
        if not data:
            # om data �r None s�tts inte instansens v�rden h�r
            return
        else:
            self.copyFromDict(data)
            
    def __repr__(self):
        "Returnerar en exakt beskrivning av aktuell h�ndelse"
        return str(self.__id) + str(self.date) + str(self.begin) + str(self.end) +\
            str(self.location) + unicode(self.course) + str(self.type) + self.group + str(self.seriesno)

    def __str__(self):
        return unicode(self).encode("latin_1")

    def __unicode__(self):
        "Returnerar en beskrivning av aktuell h�ndelse, ex. 'Kursnamn �7 grp 3 (401)'"

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
        "Kopierar tid, plats och datum fr�n annan aktivitet"

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
            # �ven tidsst�mpel f�r n�r schemat genererades inkluderas
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
        data = self.parser.parse(summary)

        self.type = data["type"]
        self.group = data["group"]
        self.seriesno = data["seriesno"]
        if not self.location:
            # om inte copyFromDict redan satt lokalen,
            # som den g�r f�r Daisy-aktiviteter
            self.location = data["location"]

        try:
            if not self.course:
                # om inte copyFromDict redan satt kursen,
                # som den g�r om kursen anges explicit
                self.course = self.timetable.getCourseByCode(data["course"])
        except ValueError:
            "Testar alternativa s�tt att hitta r�tt kurs f�r aktivitet"

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
            om flera kurser har samma namn h�mtas den (om n�gon)
            som redan finns i kurslistan.
        """

        if self.cachedcourselist.isEmpty():
            self.cachedcourselist.readFromFile()

        for course in self.cachedcourselist.getAllMatchingName(name):
            if self.timetable.hasCourse(course):
                return self.timetable.getCourseByCode(course)

        return None

    def _findTimeEditCourse(self, codes):
        "Hittar en TimeEdit-kurs genom att prova alla i en lista"

        for code in codes.split(","):
            if self.timetable.hasCourse(code):
                return self.timetable.getCourseByCode(code)

        return None

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
            Tar bort Daisy-prefixen H�rsal och �vningssal f�r
            kurser p� Valhallav�gen samt m�jligg�r �vers�ttning
            av spr�kspecifika ord som Sal, Aulan etc.
        """

        location = location.replace(u"�vningssal ", "")
        location = location.replace(u"H�rsal ", "")
        location = location.replace(u"Sal", U_("Room"))
        location = location.replace(u"Aulan", U_("Great Hall"))
        return location

    def getDescriptionWithoutLocation(self):
        description = ""
        if self.course:
            description = self.course.name + " "

        if self.type == u"F�rel�sning": description += U_("Lect")
        elif self.type == u"�vning": description += U_("Tut")
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
            Om h�ndelsens grupp �r tom �r den inte gruppindelad och ska visas.
            Om vald grupp �r tom ska alla grupper visas.
            Om vald grupp �r lika med h�ndelsens grupp ska den visas.
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
    def __init__(self, timetable, list = None):
        self.events = {}
        self.timetable = timetable
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
            Returnerar alla aktiviteter som h�r till det
            aktuella schemat; dvs. som inte �r "prenumererade"
        """

        events = []
        for event in self.getAll():
            if not isinstance(event, subscription.SubscribedEvent):
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
        "Returnerar alla h�ndelser f�r en viss kurs, utan h�nsyn till gruppval"
        
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
        "Tar bort alla h�ndelser f�r en viss kurs"

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
            L�gger till en aktivitet. ID �r en unik nyckel i listan.
            Nya aktiviteter med ID som redan existerar skriver
            _inte_ �ver existerande aktiviteter.
        """

        if self.hasEvent(event.getID()):
            # kopierar tid, plats och datum fr�n ny aktivitet
            # till existerande
            self.getEvent(event.getID()).copyDetails(event)
        else:
            # aktiviteten �r ny, l�gg bara till
            self.events[event.getID()] = event

        return self.getEvent(event.getID())

    def addEvent(self, event, course = None):
        if not isinstance(event, Event):
            try:
                if course:
                    # en kurs �r angiven explicit, ex. i webb-gr�nssnittet
                    # eller f�r "prenumererade" h�ndelser fr�n webben
                    event["course"] = course

                event = Event(self.timetable, event)
            except ValueError, e:
                # n�r en h�ndelse skapas som inte h�r till n�gon
                # k�nd kurs avbryts inte all inl�sning utan just
                # den h�ndelsen ignoreras
                import sys
                sys.stderr.write("\n" + str(e) + "\n")
                return

        EventCleaner().mark(self._add(event))

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
        Rensar borttagna h�ndelser enligt Mark-Sweep-algoritmen.

        Varje uppdaterad h�ndelse som h�mtats fr�n schemaservern
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
            if not isinstance(event, subscription.SubscribedEvent)\
            and not event.flag == self.okflag:
                timetable.removeEvent(event.getID())


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
        data = vcalendar.Writer(self.encoding).write(events)

        try:
            file(filename, "w+").writelines(data)
        except IOError:
            raise error.WriteError(U_("Could not write to"), filename)



# -----------------------------------------------------------
class HTMLExporter:

    def generate(self, timetable, fromdate, todate):
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
        return self.html.encode("utf8")

    def export(self, filename, timetable, fromdate, todate):
        self.generate(timetable, fromdate, todate)
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
    "Exporterar schema till komma-separerad lista f�r ex. JPilot"
    
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
import subscription # "timetable" m�ste laddas innan "subscription" kan laddas
