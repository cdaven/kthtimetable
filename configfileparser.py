# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import ConfigParser
import error
from i18n import *

# -----------------------------------------------------------
class ConfigParserX(ConfigParser.SafeConfigParser):
    """
        En n�got modifierad variant av "INI-filsl�sare".

        Filerna �r p� typen

            [sektion]
            nyckel = v�rde
    """

    import re

    # g�r v�nsterledet "case sensitive" och l�ter
    # det ocks� inneh�lla ':' (avgr�nsare m�ste vara '=')
    # eftersom kursnamn kan inneh�lla ':'.
    OPTCRE = re.compile(
        r'(?P<option>[^=\s][^=]*)'
        r'\s*(?P<vi>[=])\s*'
        r'(?P<value>.*)$'
        )

    # ist�llet f�r att f�lten ska skrivas med gemener
    # skrivs de helt enkelt som de �r (i str�ngrepresentation)
    # (pekar om funktionen optionxform(option) till str(option))
    optionxform = str

    # en wrapper-metod som returnerar v�rdet som Unicode
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

    # en wrapper-metod som sparar Unicode-v�rdet som Latin-1
    def set(self, section, key, value):
        if isinstance(section, unicode):
            section = section.encode("latin_1")
        if isinstance(key, unicode):
            key = key.encode("latin_1")
        if isinstance(value, unicode):
            value = value.encode("latin_1")

        ConfigParser.SafeConfigParser.set(self, section, key, str(value))

