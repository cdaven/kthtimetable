# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

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
        "Factorymetod för flera HolidayGenerator"

        self.holidays = {}
        self.otherdays = {}

        if id == "SWE":
            self.generator = SweHolidays()
            self.holidays[Date().getYear()] = self.generator.generate(Date().getYear())
            self.otherdays[Date().getYear()] = self.generator.generateOther(Date().getYear())
        else:
            raise ValueError("The holiday generator " + str(id) + "does not exist")

    def checkHoliday(self, date):
        """
            Jämför angivet datum med alla inlagda helgdagar
            och returnerar namnet på helgdagen eller False
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
            Jämför angivet datum med alla inlagda specialdagar
            och returnerar namnet på den eller False
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
    "Superklass för helgdagar: ärv för att skapa nya uppsättningar"

    def getEaster(self, year):
        "Formel för att räkna ut påskdagen"
        
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
            Ger den första 'weekday' efter 'start'
            ex. den första lördagen efter ett visst datum
        """
        for add in range(7):
            if (start + add).getWeekDay() == weekday:
                return start + add
        
        return None

    def getFirstWeekdayBefore(self, start, weekday):
        for add in range(7):
            if (start - add).getWeekDay() == weekday:
                return start - add
        
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
        """
    
        holidays = []
        easter = self.getEaster(year)
        midsummer = self.getMidsummer(year)
        halloween = self.getHalloween(year)

        # rörliga helgdagar
        holidays.append(Holiday(easter - 2, U_("Good Friday")))
        holidays.append(Holiday(easter, U_("Easter Day")))
        holidays.append(Holiday(easter + 1, U_("Easter Monday")))
        holidays.append(Holiday(easter + 39, U_("Ascension Day")))
        holidays.append(Holiday(easter + 49, U_("Whitsunday")))
        holidays.append(Holiday(midsummer, U_("Midsummer Day")))
        holidays.append(Holiday(halloween, U_("All Saints' Day")))

        yearstr = str(year)

        # fasta helgdagar
        holidays.append(Holiday(Date(yearstr + "0101"), U_("New Year's Day")))
        holidays.append(Holiday(Date(yearstr + "0106"), U_("Epiphany")))
        holidays.append(Holiday(Date(yearstr + "0501"), U_("May 1st")))
        holidays.append(Holiday(Date(yearstr + "0606"), U_("Sweden's National Day")))
        holidays.append(Holiday(Date(yearstr + "1225"), U_("Christmas Day")))
        holidays.append(Holiday(Date(yearstr + "1226"), U_("Boxing Day")))
        
        return holidays

    def generateOther(self, year):
        "Speciella dagar som inte är 'röda', dvs helgdagar."

        holidays = []

        easter = self.getEaster(year)
        midsummer = self.getMidsummer(year)

        mothersday = self.getFirstWeekdayBefore(Date(str(year) + "0531"), SUN)
        fathersday = self.getFirstWeekdayAfter(Date(str(year) + "1108"), SUN)

        # rörliga
        holidays.append(Holiday(easter - 47, U_("Shrove Tuesday")))
        holidays.append(Holiday(easter - 3, U_("Maundy Thursday")))
        holidays.append(Holiday(easter - 1, U_("Easter Eve")))
        holidays.append(Holiday(easter + 48, U_("Whitsun Eve")))
        holidays.append(Holiday(midsummer - 1, U_("Midsummer Eve")))
        holidays.append(Holiday(mothersday, U_("Mother's Day")))
        holidays.append(Holiday(fathersday, U_("Father's Day")))

        yearstr = str(year)

        # fasta
        holidays.append(Holiday(Date(yearstr + "0128"), U_("The King's Name-Day")))
        holidays.append(Holiday(Date(yearstr + "0214"), U_("St. Valentine's Day")))
        holidays.append(Holiday(Date(yearstr + "0308"), U_("International Women's Day")))
        holidays.append(Holiday(Date(yearstr + "0312"), U_("The Crown Princess' Name-Day")))
        holidays.append(Holiday(Date(yearstr + "0430"), U_("The King's Birthday")))
        holidays.append(Holiday(Date(yearstr + "0714"), U_("The Crown Princess' Birthday")))
        holidays.append(Holiday(Date(yearstr + "0808"), U_("The Queen's Name-Day")))
        holidays.append(Holiday(Date(yearstr + "1024"), U_("United Nations Day")))
        holidays.append(Holiday(Date(yearstr + "1106"), U_("The Gustavus Adolphus Day")))
        holidays.append(Holiday(Date(yearstr + "1210"), U_("The Alfred Nobel Day")))
        holidays.append(Holiday(Date(yearstr + "1213"), U_("Lucia Day")))
        holidays.append(Holiday(Date(yearstr + "1223"), U_("The Queen's Birthday")))
        holidays.append(Holiday(Date(yearstr + "1224"), U_("Christmas Eve")))
        holidays.append(Holiday(Date(yearstr + "1231"), U_("New Year's Eve")))
        try:
            holidays.append(Holiday(Date(yearstr + "0229"), U_("Intercalary Day")))
        except ValueError:
            pass

        return holidays
