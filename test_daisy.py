#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import daisy
import timetable
import calendar
import error
import xunittest

# -----------------------------------------------------------
class DaisySummaryParserTest(xunittest.TestCase):
    parser = None
    
    cases = []
    casetypes = []
    caseseriesnos = []
    casegroups = []
    casecourses = []
    
    def setUp(self):
        self.parser = daisy.SummaryParser()       
        self.cases.append("Föreläsning 1 432 - 2G1509")
        self.cases.append("Övning 4 grp 1 532 - 2G1516 IT")
        self.cases.append("Redovisning 5 402,503,504,511,512 - ITK1:KAK")
        self.cases.append("Salsskrivning Forum, Kista - 2G1524")
        self.cases.append("Föreläsning 1 Sal A - SPÖK , kvällskurs")
        self.cases.append("Salsskrivning 502,510,Sal C - 2C1225")
        self.cases.append("Handledarens rum Forum, Kista - *:59/2I1140/2I1274/2D1003")
        
        self.casetypes.append("Föreläsning")
        self.casetypes.append("Övning")
        self.casetypes.append("Redovisning")
        self.casetypes.append("Salsskrivning")
        self.casetypes.append("Föreläsning")
        self.casetypes.append("Salsskrivning")
        self.casetypes.append("Handledarens rum")

        self.caseseriesnos.append(1)
        self.caseseriesnos.append(4)
        self.caseseriesnos.append(5)
        self.caseseriesnos.append(0)
        self.caseseriesnos.append(1)
        self.caseseriesnos.append(0)
        self.caseseriesnos.append(0)

        self.casegroups.append(0)
        self.casegroups.append(1)
        self.casegroups.append(0)
        self.casegroups.append(0)
        self.casegroups.append(0)
        self.casegroups.append(0)
        self.casegroups.append(0)

        self.casecourses.append("2G1509")
        self.casecourses.append("2G1516 IT")
        self.casecourses.append("ITK1:KAK")
        self.casecourses.append("2G1524")
        self.casecourses.append("SPÖK , kvällskurs")
        self.casecourses.append("2C1225")
        self.casecourses.append("*:59/2I1140/2I1274/2D1003")

    def testExtractType(self):
        for i in range(len(self.cases)):
            self.failUnlessEqual(self.parser.extractType(self.cases[i]),
                self.casetypes[i])

    def testExtractSeriesNo(self):
        for i in range(len(self.cases)):
            self.failUnlessEqual(self.parser.extractSeriesNo(self.cases[i]),
                self.caseseriesnos[i])

    def testExtractGroup(self):
        for i in range(len(self.cases)):
            self.failUnlessEqual(self.parser.extractGroup(self.cases[i]),
                self.casegroups[i])

    def testExtractCourse(self):
        for i in range(len(self.cases)):
            self.failUnlessEqual(self.parser.extractCourse(self.cases[i]),
                self.casecourses[i])

# -----------------------------------------------------------
xunittest.run()

