#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import calendar
import datetime
import xunittest

# -----------------------------------------------------------
class DateTimeTest(xunittest.TestCase):

    def testInitAndEq(self):
        self.failUnlessEqual(calendar.DateTime(), datetime.datetime.today())
        self.failUnlessEqual(calendar.DateTime("19990505171819"), datetime.datetime(1999, 5, 5, 17, 18, 19))
        self.failUnlessEqual(calendar.DateTime("20030314090909"), calendar.DateTime(datetime.datetime(2003, 3, 14, 9, 9, 9)))
        self.failUnlessEqual(calendar.DateTime(calendar.DateTime("19880606112233")), calendar.DateTime("19880606112233"))
        self.failIfEqual(calendar.DateTime("19880606112233"), "abc")
        self.failUnlessRaises(ValueError, calendar.DateTime, "200611011299aa")
    
    def testComparison(self):
        self.failUnless(calendar.DateTime("19961231010101") < calendar.DateTime("19970101010102"))
        self.failUnless(calendar.DateTime("20040726134500") <= calendar.DateTime("20040726134500"))
        self.failUnless(calendar.DateTime("20191202113639") > datetime.datetime(2000, 12, 2, 17, 14, 1))
        self.failUnless(calendar.DateTime("19990505171819") >= calendar.DateTime("19990505171819"))

    def testDate(self):
        self.failUnlessEqual(calendar.DateTime("20030712145630").getDate(), datetime.date(2003, 7, 12))
        self.failUnlessEqual(calendar.DateTime().getDate(), datetime.date.today())

# -----------------------------------------------------------
class DateTest(xunittest.TestCase):
    
    def testInitAndEq(self):
        self.failUnlessEqual(calendar.Date(), datetime.date.today())
        self.failUnlessEqual(calendar.Date(datetime.date(2003, 7, 7)), datetime.date(2003, 7, 7))
        self.failUnlessEqual(calendar.Date("20030707"), datetime.date(2003, 7, 7))
        self.failUnlessEqual(calendar.Date(calendar.Date("19910111")), calendar.Date("19910111"))
        self.failIfEqual(calendar.Date("20030707"), "abc")
        self.failUnlessRaises(ValueError, calendar.Date, "200399aa")
        
    def testStr(self):
        self.failUnlessEqual(str(calendar.Date("20000202")), "20000202")
        self.failUnlessEqual(str(calendar.Date("20200110")), "20200110")
        
    def testAddAndSub(self):
        d1 = calendar.Date() + 3
        d2 = datetime.date.today() + datetime.timedelta(3)
        self.failUnlessEqual(d1, d2, "addition")

        d1 = calendar.Date() - 1
        d2 = datetime.date.today() - datetime.timedelta(1)
        self.failUnlessEqual(d1, d2, "subtraktion")

        self.failUnlessEqual(calendar.Date() - (calendar.Date() - 3), 3, "dagskillnad")
        self.failUnlessEqual(calendar.Date("20041118") - calendar.Date("20050105"), -48)
        self.failUnlessEqual(calendar.Date("20041118") - datetime.date(2005, 1, 5), -48)
        
    def testLastMondayOrNextIfWeekend(self):
        self.failUnlessEqual(calendar.Date("19971101").getLastMondayOrNextIfWeekend(),
                calendar.Date("19971103"))
        self.failUnlessEqual(calendar.Date("20010101").getLastMondayOrNextIfWeekend(),
                calendar.Date("20010101"))
        self.failUnlessEqual(calendar.Date("20040728").getLastMondayOrNextIfWeekend(),
                calendar.Date("20040726"))
        self.failUnlessEqual(calendar.Date("20061230").getLastMondayOrNextIfWeekend(),
                calendar.Date("20070101"))
        self.failUnlessEqual(calendar.Date("19941231").getLastMondayOrNextIfWeekend(),
                calendar.Date("19950102"))
                
    def testLastSunday(self):
        self.failUnlessEqual(calendar.Date("20040331").getLastSunday(), calendar.Date("20040328"))
        self.failUnlessEqual(calendar.Date("20101031").getLastSunday(), calendar.Date("20101031"))
        
    def testDaylightSavingTime(self):
        self.failUnless(calendar.Date("20060612").isDaylightSavingTime())
        self.failUnless(calendar.Date("20020331").isDaylightSavingTime())
        self.failUnless(calendar.Date("20031025").isDaylightSavingTime())
        self.failIf(calendar.Date("20031026").isDaylightSavingTime())
        self.failIf(calendar.Date("20091113").isDaylightSavingTime())
        self.failIf(calendar.Date("20000323").isDaylightSavingTime())
        
    def testDaylightSavingBegin(self):
        self.failUnlessEqual(calendar.Date("20040716").getDaylightSavingBegin(), calendar.Date("20040328"))
        self.failUnlessEqual(calendar.Date("19960101").getDaylightSavingBegin(), calendar.Date("19960331"))
        
    def testDaylightSavingEnd(self):
        self.failUnlessEqual(calendar.Date("20051016").getDaylightSavingEnd(), calendar.Date("20051030"))
        self.failUnlessEqual(calendar.Date("20091230").getDaylightSavingEnd(), calendar.Date("20091025"))

# -----------------------------------------------------------
class TimeTest(xunittest.TestCase):
    
    def testInitAndEq(self):
        self.failUnlessEqual(calendar.Time(), datetime.datetime.today().time())
        self.failUnlessEqual(calendar.Time("235959"), datetime.time(23, 59, 59))
        self.failUnlessEqual(calendar.Time("090909"), calendar.Time(datetime.time(9, 9, 9)))
        self.failUnlessEqual(calendar.Time(calendar.Time("112233")), calendar.Time("112233"))
        self.failIfEqual(calendar.Time("123456"), "abc")
        self.failUnlessRaises(ValueError, calendar.Time, "1299aa")
        self.failUnlessEqual(calendar.Time(11701), calendar.Time("031501"))
        
    def testComparison(self):
        self.failUnless(calendar.Time("010101") < calendar.Time("010102"))
        self.failUnless(calendar.Time("134500") <= calendar.Time("134500"))
        self.failUnless(calendar.Time("120239") > datetime.time(0, 59, 59))
        self.failUnless(calendar.Time("171819") >= calendar.Time("171819"))
    
    def testSubtraction(self):
        self.failUnlessAlmostEqual(calendar.Time("130101") - calendar.Time("083344"), 4.45472, 5)
        self.failIf(calendar.Time("101010") - calendar.Time("101010"))
        self.failUnlessEqual(calendar.Time("145507") - 8, calendar.Time("145459"))
        
    def testTimeInSeconds(self):
        self.failUnlessEqual(calendar.Time("001000").getTimeInSeconds(), 600)
        self.failUnlessEqual(calendar.Time("192519").getTimeInSeconds(), 69919)

# -----------------------------------------------------------
xunittest.run()

