# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2005

import timetable
import calendar
import settings

upload_url = "http://kthtimetable.sourceforge.net/cgi-bin/upload.py"
fetch_url = "http://kthtimetable.sourceforge.net/cgi-bin/fetch.py"

# -----------------------------------------------------------
class Subscription:

    def __init__(self, timetable):
        self.timetable = timetable

    def get(self, userid):
        import urllib
        global fetch_url

        course = SubscribedCourse(userid)
        self.timetable.addCourse(course)
        self.timetable.importOneCourse(urllib.urlopen(fetch_url +
            urllib.quote_plus(userid)).readlines(), course)

        # ändrar alla hämtade Event till SubscribedEvent
        for event in self.timetable.getAllEventsForCourse(course):
            newevent = SubscribedEvent(event)
            self.timetable.removeEvent(event.getID())
            self.timetable.addEvent(newevent)

    def remove(self, userid):
        try:
            course = self.timetable.getCourse(userid)
            self.timetable.removeCourseEvents(course)
            self.timetable.removeCourse(userid)
        except ValueError, e:
            pass

    def put(self):
        import urllib
        from email.MIMEText import MIMEText
        global upload_url

        if settings.publish and settings.publish_userid:
            vars = urllib.urlencode({"courselist": self.timetable.pickleCourses(), "username": settings.publish_userid})
            if urllib.urlopen(upload_url, vars).read().endswith("OK"):
                return True

        return False


# -----------------------------------------------------------
class Group:

    def __init__(self, name, members = []):
        newmembers = []
        for member in members:
            if not isinstance(member, unicode):
                member = unicode(member, "latin_1")
            newmembers.append(member)

        self._name = name
        self._members = newmembers
        self._visible = False

    def __str__(self):
        memberstring = ""
        for member in self._members:
            memberstring += member.encode("latin_1") + "|"
        return memberstring[:-1]

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getMembers(self):
        return self._members

    def setMembers(self, members):
        self._members = members

    def show(self, timetable):
        ss = Subscription(timetable)
        for member in self._members:
            ss.get(member)
        
        EventCompresser().compress(timetable)
        self._visible = True

    def hide(self, timetable):
        ss = Subscription(timetable)
        for member in self._members:
            ss.remove(member)

        self._visible = False

    def isVisible(self):
        return self._visible

    def copyStatus(self, other):
        self._visible = other.isVisible()


# -----------------------------------------------------------
class EventCompresser:
    """
        Minimerar det visuella utrymme som krävs för prenumererade
        händelser genom att slå ihop överlappande eller angränsande händelser.
    """

    def _getallevents(self, timetable):
        events = []
        for event in timetable.getAllEvents():
            if isinstance(event, SubscribedEvent):
                events.append(event)
        return events

    def _geteventsfordate(self, timetable, date):
        events = []
        for event in timetable.getEventsForDate(date):
            if isinstance(event, SubscribedEvent):
                events.append(event)
        return events

    def compress(self, timetable):
        already = []
        remove = []
        for event1 in self._getallevents(timetable):
            if event1 in already: continue
            for event2 in self._geteventsfordate(timetable, event1.date):
                if event1 is event2 or event2 in already:
                    continue

                if event1.overlapsOrBorders(event2):
                    # tar bort den ena händelsen och kopierar
                    # dess namn till den kvarvarande
                    event1.combineWith(event2)
                    remove.append(event2.getID())
                    already.extend([event1, event2])

        for id in remove:
            try:
                timetable.removeEvent(id)
            except ValueError:
                pass


# -----------------------------------------------------------
class SubscribedCourse(timetable.Course):
    "En 'kurs' för prenumererade aktiviteter"

    def __init__(self, code):
        timetable.Course.__init__(self, code, code)

    def __unicode__(self):
        return self.name

    def isTimeEdit(self):
        return False


# -----------------------------------------------------------
class SubscribedEvent(timetable.Event):
    """
        En aktivitet som inte kommer direkt från Daisy eller TimeEdit
        utan är importerad/prenumererad från annan källa.
    """

    def __init__(self, event):
        timetable.Event.__init__(self, None)

        self.__id = event.getID()
        self.course = event.course
        self.date = event.date
        self.begin = event.begin
        self.end = event.end
        self.type = u"Föreläsning"
        self.names = [unicode(event.course)]

    def __unicode__(self):
        string = ""
        for name in self.names:
            string += unicode(name) + " + "
        return string[:-3]

    def overlapsOrBorders(self, other):
        if self.date == other.date:
            if self.begin <= other.begin and self.end >= other.begin:
                return True
            elif other.begin <= self.begin and other.end >= self.begin:
                return True
            
        return False

    def combineWith(self, other):
        self.addNamesFrom(other)
        self.begin = min(self.begin, other.begin)
        self.end = max(self.end, other.end)

    def addNamesFrom(self, event):
        for name in event.names:
            if not name in self.names:
                self.names.append(name)

    def copyDetails(self, other):
        pass

    def getID(self):
        return self.__id

    def isGroupChosen(self):
        return True

    def toggleActive(self):
        pass

