#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import timeedit
import xunittest

# -----------------------------------------------------------
class TimeEditSummaryParserTest(xunittest.TestCase):
    
    def setUp(self):
        self.parser = timeedit.SummaryParser()
    
    def testLocation(self):
        self.failUnlessEqual(self.parser.extractLocation("M4MEK T4MEK V4BKO 5C1850.WS V26t ---"), "V26t")
        self.failUnlessEqual(self.parser.extractLocation("2D1252.L D4D E4E F4F 5V5Vio"), "5V5Vio")
        self.failUnlessEqual(self.parser.extractLocation("2C1224.F D4D E4E M4MSY T4MSY F3"), "F3")
        self.failUnlessEqual(self.parser.extractLocation("4D1225.Sem X3X"), "")
        self.failUnlessEqual(self.parser.extractLocation("D2D I2FIM I3KSI 5B1506.TEN E31 E32 E33 E34 E35 E36 V32 V33 V..."), "E31,E32,E33,E34,E35,E36,V32,V33")
        self.failUnlessEqual(self.parser.extractLocation("D2D I2FIM I3KSI 5B1506.Ö Q31 Q32 Q33 Q34"), "Q31,Q32,Q33,Q34")

    def testCourse(self):
        self.failUnlessEqual(self.parser.extractCourse("M4MEK T4MEK V4BKO 5C1850.WS V26t ---"), "5C1850")
        self.failUnlessEqual(self.parser.extractCourse("2D1252.L D4D E4E F4F 5V5Vio"), "2D1252")
        self.failUnlessEqual(self.parser.extractCourse("*:59/2I1140.TEN D4D 5V5Vio"), "*:59/2I1140")
        self.failUnlessEqual(self.parser.extractCourse("#4D1225.Sem X3X"), "4D1225")
        self.failUnlessEqual(self.parser.extractCourse("D2D I2FIM I3KSI 5B1506.Ö Q31 Q32 Q33 Q34"), "5B1506")

    def testType(self):
        self.failUnlessEqual(self.parser.extractType("M4MEK T4MEK V4BKO 5C1850.WS V26t ---"), "Workshop")
        self.failUnlessEqual(self.parser.extractType("2D1252.L D4D E4E F4F 5V5Vio"), "Laboration")
        self.failUnlessEqual(self.parser.extractType("4D1225.Sem X3X"), "Seminarium")
        self.failUnlessEqual(self.parser.extractType("D2D I2FIM I3KSI 5B1506.TEN E31 E32 E33 E34 E35 E36 V32 V33 V..."), "Tentamen")
        self.failUnlessEqual(self.parser.extractType("D2D I2FIM I3KSI 5B1506.Ö Q31 Q32 Q33 Q34"), "Övning")
        self.failUnlessEqual(self.parser.extractType("4D1225.QWERTY"), "QWERTY")

# -----------------------------------------------------------
xunittest.run()

