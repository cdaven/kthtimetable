#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import os
import os.path
import sys
import inspect

class ClassAndMethodAnalyser:
    def analyse(self, module):
        self.analyseClasses(module)

    def analyseClass(self, classtuple):
        methods = self.getMethods(classtuple[1])
        print "\n= " + classtuple[0] + " (" + str(len(methods)) + " metoder)"
        if len(methods) > 10:
            print "  * VARNING! Klassen innehåller många metoder"

        for method in methods:
            self.analyseMethod(method)

    def countLines(self, lines):
        count = 0
        for line in lines:
            line = line.strip()
            if line == "" or line.startswith("#") or line.startswith("class") or line.startswith("def"):
                continue
            count += 1
        return count

    def analyseMethod(self, methodtuple):
        try:
            code = inspect.getsourcelines(methodtuple[1])[0]
        except TypeError:
            return

        print "    - " + methodtuple[0] + " (" + str(self.countLines(code)) + " rader)"
        if self.countLines(code) > 10:
            print "  * VARNING! Metoden är lång"

    def analyseClasses(self, module):
        module = __import__(module)
        members = inspect.getmembers(module)
        for member in members:
            if inspect.isclass(member[1]):
                self.analyseClass(member)

    def getMethods(self, classname):
        # returnerar även superklassernas metoder ...
        members = inspect.getmembers(classname)
        methods = []
        for member in members:
            if inspect.ismethod(member[1]):
                print member
                methods.append(member)

        return methods

analyser = ClassAndMethodAnalyser()

def runfile(file):
    if os.system("python " + file):
        sys.exit(1)

for file in os.listdir(os.getcwd()):
    if os.path.isdir(file):
        continue
    
    file = os.path.split(file)[1]
    
    if file == __file__:
        continue
    
    if file.startswith("test_") and file.endswith(".py"):
        print "=== " + file
        runfile(file)
#    elif file.endswith(".py") or file.endswith(".pyw"):
#        print "=== " + file
#        analyser.analyse(os.path.splitext(file)[0])
    
    
