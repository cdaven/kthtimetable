# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import unittest

def run():
    unittest.main()

# -----------------------------------------------------------
class TestCase(unittest.TestCase):
    def failUnlessListsEqual(self, list1, list2, msg=None):
        """
            Jämför listor så att varje elements representation
            måste finnas i den andra listan. Ordningen
            spelar dock ingen roll.
        """
        
        equal = False
        if self.compareListsByRepresentation(list1, list2):
            equal = True
        elif self.compareLists(list1, list2):
            equal = True
            
        if not equal:        
            raise self.failureException("Listorna är inte lika. (" + str(msg) + ")")
        
    def compareLists(self, list1, list2):
        for e in list1:
            if e not in list2:
                return False
            
        return True

    def compareListsByRepresentation(self, list1, list2):
        nlist1 = []
        nlist2 = []

        for e in list1:
            nlist1.append(repr(e))
        for e in list2:
            nlist2.append(repr(e))

        for e in nlist1:
            if e not in nlist2:
                return False
            
        return True
    
