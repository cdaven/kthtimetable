# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

from calendar import *
from i18n import *

# -----------------------------------------------------------
class Holiday:
    "En helgdag med datum och namn"

    def __init__(self, date, name):
        self.date = date
        self.name = name
        
    def __repr__(self):
        return str(self.date) + ": " + self.name

# -----------------------------------------------------------
class HolidayChecker:
    def __init__(self, id):
        "Factorymetod f�r flera HolidayGenerator"

        self.holidays = {}
        self.otherdays = {}

        if id == "SWE":
            self.generator = SweHolidays()
            self.holidays[Date().getYear()] = self.generator.generate(Date().getYear())
            self.otherdays[Date().getYear()] = self.generator.generateOther(Date().getYear())
        else:
            raise ValueError(U_("Helgdagsgeneratorn") + " " + str(id) + " " + U_("finns inte."))

    def checkHoliday(self, date):
        """
            J�mf�r angivet datum med alla inlagda helgdagar
            och returnerar namnet p� helgdagen eller False
            om ej helgdag.
        """
        
        year = date.getYear()
        if year not in self.holidays.keys():
            self.holidays[year] = self.generator.generate(year)
    
        for holiday in self.holidays[year]:
            if date == holiday.date:
                return holiday.name

        return False

    def checkOther(self, date):
        """
            J�mf�r angivet datum med alla inlagda specialdagar
            och returnerar namnet p� den eller False
            om ej helgdag.
        """
        
        year = date.getYear()
        if year not in self.otherdays.keys():
            self.otherdays[year] = self.generator.generateOther(year)
    
        for holiday in self.otherdays[year]:
            if date == holiday.date:
                return holiday.name
        
        return False


# -----------------------------------------------------------
class HolidayGenerator:
    "Superklass f�r helgdagar: �rv f�r att skapa nya upps�ttningar"

    def getEaster(self, year):
        "Formel f�r att r�kna ut p�skdagen"
        
        c = year / 100
        n = year - 19 * ( year / 19 )
        k = ( c - 17 ) / 25
        i = c - c / 4 - ( c - k ) / 3 + 19 * n + 15
        i = i - 30 * ( i / 30 )
        i = i - ( i / 28 ) * ( 1 - ( i / 28 ) * ( 29 / ( i + 1 ) ) * ( ( 21 - n ) / 11 ) )
        j = year + year / 4 + i + 2 - c + c / 4
        j = j - 7 * ( j / 7 )
        l = i - j
        m = 3 + ( l + 40 ) / 44
        d = l + 28 - 31 * ( m / 4 )
        
        month = str(m)
        if m < 10: month = "0" + month
        day = str(d)
        if d < 10: day = "0" + day
        
        return Date(str(year) + month + day)

    def getFirstWeekdayAfter(self, start, weekday):
        """
            Ger den f�rsta 'weekday' efter 'start'
            ex. den f�rsta l�rdagen efter ett visst datum
        """
        for add in range(7):
            if (start + add).getWeekDay() == weekday:
                return start + add
        
        return None

# -----------------------------------------------------------
class SweHolidays(HolidayGenerator):
    def getHalloween(self, year):
        "Tar fram alla helgons dag"
    
        return self.getFirstWeekdayAfter(Date(str(year) + "1031"), SAT)

    def getMidsummer(self, year):
        "Tar fram midsommardagen"
    
        return self.getFirstWeekdayAfter(Date(str(year) + "0620"), SAT)

    def generate(self, year):
        """
            Tar fram en lista med alla svenska helgdagar.
            �n s� l�nge endast de som kan infalla p� vardag.
        """
    
        holidays = []
        easter = self.getEaster(year)
        midsummer = self.getMidsummer(year)

        yearstr = str(year)
        
        # r�rliga helgdagar
        holidays.append(Holiday(easter - 2, U_("Langfredag")))
        holidays.append(Holiday(easter + 1, U_("Annandag pask")))
        holidays.append(Holiday(easter + 39, U_("Kristi himmelsfards dag")))
        holidays.append(Holiday(easter + 51, U_("Annandag pingst")))
        holidays.append(Holiday(midsummer - 1, U_("Midsommarafton")))

        # fasta helgdagar
        holidays.append(Holiday(Date(yearstr + "0101"), U_("Nyarsdagen")))
        holidays.append(Holiday(Date(yearstr + "0106"), U_("Trettondedag jul")))
        holidays.append(Holiday(Date(yearstr + "0501"), U_("Forsta maj")))
        holidays.append(Holiday(Date(yearstr + "1224"), U_("Julafton")))
        holidays.append(Holiday(Date(yearstr + "1225"), U_("Juldagen")))
        holidays.append(Holiday(Date(yearstr + "1226"), U_("Annandag jul")))
        
        return holidays

    def generateOther(self, year):
        "Speciella dagar som inte �r 'r�da', dvs helgdagar."

        holidays = []
        yearstr = str(year)

        # Nationella flaggdagar som inte ocks� �r helgdagar
        holidays.append(Holiday(Date(yearstr + "0128"), U_("Konungens namnsdag")))
        holidays.append(Holiday(Date(yearstr + "0312"), U_("Kronprinsessans namnsdag")))
        holidays.append(Holiday(Date(yearstr + "0430"), U_("Konungens fodelsedag")))
        holidays.append(Holiday(Date(yearstr + "0606"), U_("Sveriges nationaldag")))
        holidays.append(Holiday(Date(yearstr + "0714"), U_("Kronprinsessans fodelsedag")))
        holidays.append(Holiday(Date(yearstr + "0808"), U_("Drottningens namnsdag")))
        holidays.append(Holiday(Date(yearstr + "1024"), U_("FN-dagen")))
        holidays.append(Holiday(Date(yearstr + "1106"), U_("Gustav Adolfsdagen")))
        holidays.append(Holiday(Date(yearstr + "1210"), U_("Nobeldagen")))
        holidays.append(Holiday(Date(yearstr + "1223"), U_("Drottningens fodelsedag")))

        return holidays
