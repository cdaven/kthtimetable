#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

from i18n import *
setLanguage("en")

import timeedit
import xunittest

# -----------------------------------------------------------
class TimeEditSummaryParserTest(xunittest.TestCase):
    
    def setUp(self):
        self.parser = timeedit.SummaryParser()
        self.summary1 = "9E1300, Le, H21"
        self.summary2 = "5B1101, 5B1108, 5B1109, 5B1110, 5B1128, 5B1139, 5B1307, TEN, V01, V11, V21, V22, V23, V32, V34"
        self.summary3 = "3B1720, Frl, --, FB51, FB52"
        self.summary4 = "5A1312.c, Ovn"
        self.summary5 = "3B1750, Q1"

    def testLocation(self):
        self.failUnlessEqual(self.parser.extractLocation(self.summary1), "H21")
        self.failUnlessEqual(self.parser.extractLocation(self.summary2), "V01,V11,V21,V22,V23,V32,V34")
        self.failUnlessEqual(self.parser.extractLocation(self.summary3), "FB51,FB52")
        self.failUnlessEqual(self.parser.extractLocation(self.summary4), "")
        self.failUnlessEqual(self.parser.extractLocation(self.summary5), "Q1")

    def testCourseAndGroup(self):
        self.failUnlessEqual(self.parser.extractCourseAndGroup(self.summary1), ("9E1300", ""))
        self.failUnlessEqual(self.parser.extractCourseAndGroup(self.summary2), ("5B1101,5B1108,5B1109,5B1110,5B1128,5B1139,5B1307", ""))
        self.failUnlessEqual(self.parser.extractCourseAndGroup(self.summary3), ("3B1720", ""))
        self.failUnlessEqual(self.parser.extractCourseAndGroup(self.summary4), ("5A1312", "c"))
        self.failUnlessEqual(self.parser.extractCourseAndGroup(self.summary5), ("3B1750", ""))

    def testType(self):
        self.failUnlessEqual(self.parser.extractType(self.summary1), u"Lektion")
        self.failUnlessEqual(self.parser.extractType(self.summary2), u"Tentamen")
        self.failUnlessEqual(self.parser.extractType(self.summary3), u"Föreläsning")
        self.failUnlessEqual(self.parser.extractType(self.summary4), u"Övning")
        self.failUnlessEqual(self.parser.extractType(self.summary5), u"")

# -----------------------------------------------------------
xunittest.run()

