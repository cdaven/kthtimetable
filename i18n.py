# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import gettext
import sys

# Hämtar översättningsfilerna

translation = None

def getTranslation(lang):
    global translation

    try:
        translation = gettext.translation("kthtimetable", "locale", languages=[lang])
    except IOError, e:
        sys.stderr.write("Couldn't find translation for " + lang + "\n" + str(e) + "\n")
        sys.exit(1)
    
    # Sätter gränssnittets språk
    translation.install()

# konverterar språkspecifika strängar till unicode
def U_(string):
    return unicode(_(string), "utf8")

