# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import datetime
import error
from i18n import *

MON = 0
TUE = 1
WED = 2
THU = 3
FRI = 4
SAT = 5
SUN = 6

# -----------------------------------------------------------
class Date:
    WEEKDAYS = [U_("Mon"), U_("Tue"), U_("Wed"), U_("Thu"), U_("Fri"), U_("Sat"), U_("Sun")]
    MONTHS = [U_("January"), U_("February"), U_("March"), U_("April"), U_("May"), U_("June"),
            U_("July"), U_("August"), U_("September"), U_("October"), U_("November"), U_("December")]

    def __init__(self, arg=None):
        "Kan initialiseras med datetime.date, Date, str�ng eller tomt"

        if isinstance(arg, Date):
            year = arg.getYear()
            month = arg.getMonth()
            day = arg.getDay()
        elif isinstance(arg, datetime.date):
            year = arg.year
            month = arg.month
            day = arg.day
        elif (isinstance(arg, str) or isinstance(arg, unicode)) and len(arg) >= 8:
            year = int(arg[:4])
            month = int(arg[4:6])
            day = int(arg[6:8])
        else:
            year = datetime.date.today().year
            month = datetime.date.today().month
            day = datetime.date.today().day

        self.__date = datetime.date(year, month, day)

    def __str__(self):
        return self.__date.strftime("%Y%m%d")
        
    def __eq__(self, other):
        "J�mf�relse fungerar endast om en Date st�r p� v�nster sida =="
        return self.__date == Date(other).__date
        
    def __ne__(self, other):
        if self.__eq__(other): return False
        else: return True

    def __lt__(self, other):
        return self.__date < Date(other).__date

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return self.__date > Date(other).__date

    def __ge__(self, other):
        return self > other or self == other

    def __add__(self, other):
        "Returnerar Date plus s� m�nga dagar som 'other' anger"
        return Date(self.__date + datetime.timedelta(other))
        
    def __sub__(self, other):
        """
            Returnerar skillnaden i dagar mellan tv� datum
            eller motsatsen till __add__
        """
        if isinstance(other, int):
            return Date(self.__date - datetime.timedelta(other))
        else:
            return (self.__date - Date(other).__date).days
            
    def getYear(self):
        return self.__date.year

    def getMonth(self):
        return self.__date.month
    
    def getMonthName(self):
        return self.MONTHS[self.getMonth() - 1]

    def getDay(self):
        return self.__date.day
        
    def getWeekDay(self):
        return self.__date.weekday()

    def getWeekDayName(self):
        return self.WEEKDAYS[self.getWeekDay()]

    def getWeek(self):
        return self.__date.isocalendar()[1]
    
    def getNiceString(self):
        return unicode(self.getWeekDayName() + " " + str(self.getDay()) + " " + self.getMonthName() +\
            " " + str(self.getYear()))
        
    def isWeekend(self):
        return self.getWeekDay() >= SAT
        
    def isHoliday(self):
        return holidaychecker.checkHoliday(self)

    def getSpecialName(self):
        """
            Returnerar namnet p� dagen om det �r en helgdag
            eller i andra hand en flaggdag eller annat.
        """
        name = holidaychecker.checkHoliday(self)
        if name == False:
            name = holidaychecker.checkOther(self)

        return name

    def getNextMonday(self):
        return self + 7 - self.getWeekDay()
        
    def getLastMonday(self):
        return self - self.getWeekDay()

    def getLastMondayOrNextIfWeekend(self):
        if self.isWeekend():
            return self.getNextMonday()
        else:
            return self.getLastMonday()

    def isDaylightSavingTime(self):
        "�r aktuellt datum i sommartid?"
        if self >= self.getDaylightSavingBegin() and self < self.getDaylightSavingEnd():
            return True
        else:
            return False
        
    def getDaylightSavingBegin(self):
        "Sommartid b�rjar sista s�ndagen i mars"
        return Date(datetime.date(self.getYear(), 3, 31)).getLastSunday()

    def getDaylightSavingEnd(self):
        "Sommartid slutar sista s�ndagen i oktober"
        return Date(datetime.date(self.getYear(), 10, 31)).getLastSunday()
    
    def getLastSunday(self):
        return self - ((self.getWeekDay() + 1) % 7)

# -----------------------------------------------------------
class Time:
    def __init__(self, arg=None):
        if isinstance(arg, Time):
            hour = arg.getHour()
            minute = arg.getMinute()
            second = arg.getSecond()
        elif isinstance(arg, datetime.time):
            hour = arg.hour
            minute = arg.minute
            second = arg.second
        elif (isinstance(arg, str) or isinstance(arg, unicode)) and len(arg) >= 6:
            hour = int(arg[:2])
            minute = int(arg[2:4])
            second = int(arg[4:6])
        elif isinstance(arg, int):
            hour = arg / 3600
            minute = (arg - hour * 3600) / 60
            second = arg - hour * 3600 - minute * 60
        else:
            hour = datetime.datetime.today().time().hour
            minute = datetime.datetime.today().time().minute
            second = datetime.datetime.today().time().second
        
        self.__time = datetime.time(hour, minute, second)
        
    def __str__(self):
        return self.__time.strftime("%H%M%S")
        
    def __sub__(self, other):
        """
            Returnerar skillnad i sekunder mellan tidpunkter eller
            returnerar en ny tid 'other' sekunder tidigare.
        """
    
        if isinstance(other, int):
            return Time(self.getTimeInSeconds() - other)
        else:
            return (self.getTimeInSeconds() - Time(other).getTimeInSeconds()) / 3600.0

    def __eq__(self, other):
        return self.__time == Time(other).__time

    def __ne__(self, other):
        if self.__eq__(other): return False
        else: return True

    def __lt__(self, other):
        return self.__time < Time(other).__time

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return self.__time > Time(other).__time

    def __ge__(self, other):
        return self > other or self == other

    def getHour(self):
        return self.__time.hour
       
    def getMinute(self):
        return self.__time.minute

    def getSecond(self):
        return self.__time.second
    
    def getTimeInSeconds(self):
        return self.getHour() * 3600 + self.getMinute() * 60 + self.getSecond()

    def getNiceString(self):
        return self.__time.strftime("%H:%M")

# -----------------------------------------------------------
class DateTime:
    def __init__(self, arg=None):
        if isinstance(arg, datetime.datetime):
            year = arg.year
            month = arg.month
            day = arg.day
            hour = arg.hour
            minute = arg.minute
            second = arg.second
        elif (isinstance(arg, str) or isinstance(arg, unicode)) and len(arg) == 14:
            year = int(arg[:4])
            month = int(arg[4:6])
            day = int(arg[6:8])
            hour = int(arg[8:10])
            minute = int(arg[10:12])
            second = int(arg[12:])
        elif isinstance(arg, DateTime):
            year = arg.getYear()
            month = arg.getMonth()
            day = arg.getDay()
            hour = arg.getHour()
            minute = arg.getMinute()
            second = arg.getSecond()
        else:
            year = datetime.datetime.today().year
            month = datetime.datetime.today().month
            day = datetime.datetime.today().day
            hour = datetime.datetime.today().hour
            minute = datetime.datetime.today().minute
            second = datetime.datetime.today().second
        
        self.__datetime = datetime.datetime(year, month, day, hour, minute, second)
    
    def __str__(self):
        return self.__datetime.strftime("%Y%m%d%H%M%S")

    def __eq__(self, other):
        return self.__datetime == DateTime(other).__datetime

    def __lt__(self, other):
        return self.__datetime < DateTime(other).__datetime

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return self.__datetime > DateTime(other).__datetime

    def __ge__(self, other):
        return self > other or self == other
    
    def getYear(self):
        return self.__datetime.year

    def getMonth(self):
        return self.__datetime.month

    def getDay(self):
        return self.__datetime.day

    def getHour(self):
        return self.__datetime.hour

    def getMinute(self):
        return self.__datetime.minute

    def getSecond(self):
        return self.__datetime.second

    def getDate(self):
        return self.__datetime.date()
    
# -----------------------------------------------------------
from holidays import HolidayChecker
holidaychecker = HolidayChecker("SWE")
