# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import urllib
import re
import error
import calendar

def getITUCourses(input = None, callback = None):
    """
        H�mtar alla valbara kurser p� IT-universitetet f�r aktuell termin.
        Callback anv�nds f�r att visa f�rloppet f�r anv�ndaren
    """
    
    if not isinstance(input, str):
        period = getYearTerm()
        try:
            url = urllib.urlopen("http://www.it.kth.se/schema.html?termin=" + period +
                "&program=0&institution=0&Visa=Visa")
        except IOError:
            raise error.ReadError(_("Kunde inte lasa fran") + " www.it.kth.se/schema.html", "www.it.kth.se/schema.html")

        if callback: callback()
        input = url.read()

    if callback: callback()

    if len(input) == 0:
        raise error.DataError(_("Schemageneratorn gav ingen data"))

    import timetable
    all = re.findall("value=\"(\d{3,})\"[^a-z���A-Z���0-9]*(.*?) \((.*?)\)", descape(input))
    courses = []
    for a in all:
        courses.append(timetable.Course(a[2].strip(), a[1].strip(), int(a[0])))

    return courses

def getYearTerm():
    year = str(calendar.Date().getYear())
    week = calendar.Date().getWeek()

    if week > 30: term = "2" # h�sttermin
    else: term = "1" # v�rtermin

    return year + term

def descape(text):
    "�vers�tter fr�n html till specialtecken"

    text = text.replace("&#38;", "&")
    return re.sub("&(\w+?);", descape_entity, text)

def descape_entity(rx):
    "Anv�nds endast av descape() via re.sub()"

    import htmlentitydefs
    
    if rx.group(1) in htmlentitydefs.entitydefs:
        return htmlentitydefs.entitydefs[rx.group(1)]
    else:
        return rx.group(0)

# -----------------------------------------------------------
class CookieURLopener(urllib.FancyURLopener):
    """
        �ppnar URL:er och f�ngar upp kakor och 302-koder (HTTP-omdirigering)

        Skapat av Charles Anderson 2000, n�got modifierat av Christian Dav�n 2004
        Koden tillh�r "public domain"
    """
    
    def __init__(self):
        urllib.FancyURLopener.__init__(self)
        self.__cookies = []

    def open(self, url, data=None):
        """Handle an HTTP open request.
        We pass this to FancyURLopener to do
        the real work.  Afterwards, we scan the info() for
        cookies."""

        result = urllib.FancyURLopener.open(self, url, data)
        self.__eatCookies(result.info())
        return result

    def http_error_302(self, url, fp, errcode, errmsg, headers, data=None):
        """Handle an HTTP redirect.  First we get the cookies from the
        headers off of the initial URL.  Then hand it off to the super-class,
        which will call back into our open_http method, where we can pick
        up more cookies."""

        self.__eatCookies(headers)
        result = urllib.FancyURLopener.http_error_302(self, url, fp, errcode, errmsg, headers, data=None)
        return result

    def __eatCookies(self, headers):
        """Scan a set of response headers for cookies.  We add each
        cookie to our list."""

        cookies = headers.getallmatchingheaders("set-cookie")
        for c in cookies:
            self.__addCookie(c[12:].strip())        # "set-cookie: " is 11 characters

    def __addCookie(self, cookie):
        """Add a cookie to our cache of them and call addheaders of our
        parent."""

        self.__cookies.append(cookie)
        self.addheader("Cookie", cookie)
