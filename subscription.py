# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2005

import timetable
import calendar
import settings

subscription_url = "http://chrome/wap/index.py"

# -----------------------------------------------------------
class Subscription:

    def get(self, userid):
        import urllib
        global subscription_url
        course = SubscribedCourse(userid)
        timetable.courselist.addCourse(course)
        timetable.timetable.importVCalData(urllib.urlopen(subscription_url + "/fetch?" +
            urllib.quote_plus(userid)).readlines(), course)

    def remove(self, userid):
        try:
            course = timetable.courselist.getCourse(userid)
            timetable.courselist.removeCourse(userid) # tar också bort händelserna
        except ValueError:
            pass

    def put(self):
        import urllib
        from email.MIMEText import MIMEText
        global subscription_url

        if settings.publish and settings.publish_userid:
            vars = urllib.urlencode({"courselist": timetable.courselist.pickle(), "username": settings.publish_userid})
            if urllib.urlopen("http://chrome/wap/index.py/upload", vars).read() == "OK":
                return True

        return False

# -----------------------------------------------------------
class EventCompresser:
    """
        Minimerar det visuella utrymme som krävs för prenumererade
        händelser genom att slå ihop överlappande eller angränsande händelser.
    """

    def _getallevents(self):
        events = []
        for event in timetable.timetable.getAllEvents():
            if isinstance(event, SubscribedEvent):
                events.append(event)
        return events

    def _geteventsfordate(self, date):
        events = []
        for event in timetable.timetable.getEventsForDate(date):
            if isinstance(event, SubscribedEvent):
                events.append(event)
        return events

    def compress(self):
        already = []
        remove = []
        for event1 in self._getallevents():
            if event1 in already: continue
            for event2 in self._geteventsfordate(event1.date):
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
                timetable.timetable.removeEvent(id)
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

    def __init__(self, data):
        timetable.Event.__init__(self)

        self.__id = data["id"]
        self.course = data["course"]
        self.date = calendar.Date(data["date"])
        self.begin = calendar.Time(data["begin"])
        self.end = calendar.Time(data["end"])
        self.type = u"Föreläsning"

        self.names = [data["course"]]

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
        self.addNamesFrom(other)

    def getID(self):
        return self.__id

    def isGroupChosen(self):
        return True

    def toggleActive(self):
        pass

