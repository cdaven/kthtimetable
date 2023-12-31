# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import gettext
import sys

translation = None

def setLanguage(lang):
    global translation

    try:
        translation = gettext.translation("kthtimetable", "locale", languages=[lang])
    except IOError, e:
        sys.stderr.write("Couldn't find translation for " + lang + "\n" + str(e) + "\n")
        sys.exit(1)
    
    # s�tter gr�nssnittets spr�k
    translation.install()

# konverterar spr�kspecifika str�ngar till unicode
def U_(string):
    return unicode(_(string), "utf8")

