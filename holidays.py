# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

from calendar import *

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
            raise ValueError("Helgdagsgeneratorn " + str(id) + " finns inte.")

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
            Än så länge endast de som kan infalla på vardag.
        """
    
        holidays = []
        easter = self.getEaster(year)
        midsummer = self.getMidsummer(year)

        yearstr = str(year)
        
        # rörliga helgdagar
        holidays.append(Holiday(easter - 2, "Långfredag"))
        holidays.append(Holiday(easter + 1, "Annandag påsk"))
        holidays.append(Holiday(easter + 39, "Kristi himmelsfärds dag"))
        holidays.append(Holiday(easter + 51, "Annandag pingst"))
        holidays.append(Holiday(midsummer - 1, "Midsommarafton"))

        # fasta helgdagar
        holidays.append(Holiday(Date(yearstr + "0101"), "Nyårsdagen"))
        holidays.append(Holiday(Date(yearstr + "0106"), "Trettondedag jul"))
        holidays.append(Holiday(Date(yearstr + "0501"), "Första maj"))
        holidays.append(Holiday(Date(yearstr + "1224"), "Julafton"))
        holidays.append(Holiday(Date(yearstr + "1225"), "Juldagen"))
        holidays.append(Holiday(Date(yearstr + "1226"), "Annandag jul"))
        
        return holidays

    def generateOther(self, year):
        "Speciella dagar som inte är 'röda', dvs helgdagar."

        holidays = []
        yearstr = str(year)

        # Nationella flaggdagar som inte också är helgdagar
        holidays.append(Holiday(Date(yearstr + "0128"), "Konungens namnsdag"))
        holidays.append(Holiday(Date(yearstr + "0312"), "Kronprinsessans namnsdag"))
        holidays.append(Holiday(Date(yearstr + "0430"), "Konungens födelsedag"))
        holidays.append(Holiday(Date(yearstr + "0606"), "Sveriges nationaldag"))
        holidays.append(Holiday(Date(yearstr + "0714"), "Kronprinsessans födelsedag"))
        holidays.append(Holiday(Date(yearstr + "0808"), "Drottningens namnsdag"))
        holidays.append(Holiday(Date(yearstr + "1024"), "FN-dagen"))
        holidays.append(Holiday(Date(yearstr + "1106"), "Gustav Adolfsdagen"))
        holidays.append(Holiday(Date(yearstr + "1210"), "Nobeldagen"))
        holidays.append(Holiday(Date(yearstr + "1223"), "Drottningens födelsedag"))

        return holidays
