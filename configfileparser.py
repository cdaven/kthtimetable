# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import ConfigParser
import error
from i18n import *

# -----------------------------------------------------------
class ConfigParserX(ConfigParser.SafeConfigParser):
    """
        En något modifierad variant av "INI-filsläsare".

        Filerna är på typen

            [sektion]
            nyckel = värde
    """

    import re

    # gör vänsterledet "case sensitive" och låter
    # det också innehålla ':' (avgränsare måste vara '=')
    # eftersom kursnamn kan innehålla ':'.
    OPTCRE = re.compile(
        r'(?P<option>[^=\s][^=]*)'
        r'\s*(?P<vi>[=])\s*'
        r'(?P<value>.*)$'
        )

    # istället för att fälten ska skrivas med gemener
    # skrivs de helt enkelt som de är (i strängrepresentation)
    # (pekar om funktionen optionxform(option) till str(option))
    optionxform = str

    # en wrapper-metod som returnerar värdet som Unicode
    def get(self, section, key):
        try:
            return unicode(ConfigParser.SafeConfigParser.get(self, section, key), "latin_1")
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            raise error.DataError("Missing data in timetable file")

    def getstrorempty(self, section, key):
        val = ""
        if ConfigParser.SafeConfigParser.has_option(self, section, key):
            val = ConfigParser.SafeConfigParser.get(self, section, key)

        return val

    def getintorzero(self, section, key):
        val = 0
        if ConfigParser.SafeConfigParser.has_option(self, section, key):
            val = ConfigParser.SafeConfigParser.getint(self, section, key)

        return val

    def getboolean(self, section, key):
        val = True
        if ConfigParser.SafeConfigParser.has_option(self, section, key):
            val = ConfigParser.SafeConfigParser.getboolean(self, section, key)

        return val

    # en wrapper-metod som sparar Unicode-värdet som Latin-1
    def set(self, section, key, value):
        if isinstance(value, unicode):
            value = value.encode("latin_1")
        ConfigParser.SafeConfigParser.set(self, section, key, value)

