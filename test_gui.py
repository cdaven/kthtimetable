#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import gui
import timetable
import xunittest

# -----------------------------------------------------------
class EventOrganiserTest(xunittest.TestCase):
    organiser = None
    event1 = None
    event2 = None
    event3 = None
    event4 = None

    def setUp(self):
        self.organiser = gui.EventOrganiser()
        self.event1 = timetable.Event(1, begin="110000", end="130000")
        self.event2 = timetable.Event(2, begin="120000", end="150000")
        self.event3 = timetable.Event(3, begin="143000", end="170000")
        self.event4 = timetable.Event(4, begin="094500", end="110000")
        self.organiser.events.append(self.event1)
        self.organiser.events.append(self.event2)
        self.organiser.events.append(self.event3)
        self.organiser.events.append(self.event4)

    def testAddEvent(self):
        self.organiser.events = []
        self.organiser.addEvent(self.event1)
        self.event1.clashes = 0
        self.event1.column = 0
        events = [self.event1]
        self.failUnlessListsEqual(events, self.organiser.events)

        self.organiser.addEvent(self.event2)
        self.event1.clashes = 1
        self.event2.clashes = 1
        self.event2.column = 1
        events = [self.event1, self.event2]
        self.failUnlessListsEqual(events, self.organiser.events)

        self.organiser.addEvent(self.event3)
        self.event1.clashes = 2
        self.event2.clashes = 2
        self.event3.clashes = 2
        self.event3.column = 2
        events = [self.event1, self.event2, self.event3]
        self.failUnlessListsEqual(events, self.organiser.events)

        self.organiser.addEvent(self.event4)
        self.event4.clashes = 0
        self.event4.column = 0
        events = [self.event1, self.event2, self.event3, self.event4]
        self.failUnlessListsEqual(events, self.organiser.events)

    def testFitsInColumn(self):
        column = [self.event4, self.event2]
        self.failIf(self.organiser.fitsInColumn(column, self.event3))
        self.failIf(self.organiser.fitsInColumn(column, self.event1))

        column = []
        self.failUnless(self.organiser.fitsInColumn(column, self.event3))

        column = [self.event1]
        self.failUnless(self.organiser.fitsInColumn(column, self.event3))

    def testClashGroup(self):
        shouldclash = [self.event1, self.event2, self.event3]
        
        clashes = []
        self.organiser.getClashGroup(self.event1, clashes)
        self.failUnlessListsEqual(shouldclash, clashes)

        clashes = []
        self.organiser.getClashGroup(self.event4, clashes)
        self.failUnlessEqual([], clashes)

    def testClash(self):
        event1 = timetable.Event(1, begin="110000", end="130000")
        event2 = timetable.Event(1, begin="120000", end="150000")
        self.failUnless(self.organiser.isClash(event1, event2))

        event1 = timetable.Event(1, begin="090000", end="120000")
        event2 = timetable.Event(1, begin="120000", end="130000")
        self.failIf(self.organiser.isClash(event1, event2))

        event1 = timetable.Event(1, begin="093000", end="120000")
        event2 = timetable.Event(1, begin="080000", end="093300")
        self.failUnless(self.organiser.isClash(event1, event2))

# -----------------------------------------------------------
xunittest.run()
