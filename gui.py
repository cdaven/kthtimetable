# -*- coding: iso-8859-1 -*-

# Skapat av Christian Dav�n 2004

import wx
import settings
import guisettings
import calendar
import timetable
import error
from i18n import *

applicationname = "KTH TimeTable"
applicationversion = "2.1"

# -----------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        global applicationname
        global applicationversion
        
        guisettings.getSystemSettings()

        self.weeklabel = None
        self.datelabel = None
        self.daylabels = []
    
        self.currentmonday = None
        self.days = []
        
        wx.Frame.__init__(self, None, -1, applicationname + " " + applicationversion)

        settings.load()

        self.SetBackgroundColour(guisettings.bgcolour_default)
        if wx.MINOR_VERSION >= 5:
            self.ClearBackground()

        layout = wx.BoxSizer(wx.VERTICAL)

        layout.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)
        layout.Add(self.AddButtonsAndLabels(), 0, wx.ALL|wx.ALIGN_CENTRE, 10)
        layout.Add(self.AddWeekView(), 1, wx.EXPAND)

        self.AddMenu()

        self.statusbar = wx.StatusBar(self, -1, style=wx.ST_SIZEGRIP)
        layout.Add(self.statusbar, 0, wx.EXPAND)

        self.SetSizerAndFit(layout)
        self.CentreOnScreen()
        wx.EVT_CLOSE(self, self.OnClose)
 
        self.GoToday(None)

        if calendar.Date() - timetable.timetable.updated > 7:
            msg = U_("Det var over en vecka sedan du uppdaterade schemat senast. Det kan ha\nforandrats sedan dess. Vill du uppdatera schemat nu?")
            if wx.MessageDialog(self, msg, U_("Gammalt schema"),
               style=wx.YES_NO|wx.ICON_QUESTION).ShowModal() == wx.ID_YES:
                self.Update(None)

    def AddWeekView(self):
        weekview = wx.BoxSizer(wx.VERTICAL)
        hoursanddays = wx.BoxSizer(wx.HORIZONTAL)
        daynames = wx.BoxSizer(wx.HORIZONTAL)

        flag = wx.EXPAND
        if wx.MINOR_VERSION >= 5:
            flag |= wx.FIXED_MINSIZE

        hoursanddays.Add(HoursPanel(self), 0, flag)

        # ritar ut saker f�r varje veckodag
        for i in range(settings.lastweekday + 1):
            # sj�lva namnet p� dagen (fylls i senare under updateView())
            self.daylabels.append(StaticText(self, "Ons 15", size=(60, 15), style=wx.ST_NO_AUTORESIZE|wx.ALIGN_CENTRE|wx.SIMPLE_BORDER))
            self.daylabels[-1].SetBackgroundColour(guisettings.bgcolour_daylabel)

            daynames.Add(self.daylabels[-1], 1, wx.RIGHT|wx.LEFT, 1)

            # schemat f�r dagen, �tminstone utrymmet f�r detsamma
            self.days.append(DayPanel(self))
            hoursanddays.Add(self.days[-1], 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 1)
            
        weekview.Add(daynames, 0, wx.EXPAND|wx.LEFT, 60)
        weekview.Add(hoursanddays, 1, wx.EXPAND)
        return weekview
        
    def AddButtonsAndLabels(self):
        self.weeklabel = StaticText(self, "Vecka 43", size=(-1, -1), style=wx.ALIGN_CENTRE)
        self.datelabel = StaticText(self, "Juli 2004", size=(150, 25), style=wx.ST_NO_AUTORESIZE|wx.ALIGN_RIGHT)

        guisettings.font_default.SetWeight(wx.BOLD)
        guisettings.font_default.SetPointSize(guisettings.font_default.GetPointSize() + 1)
        self.datelabel.SetFont(guisettings.font_default)
        guisettings.font_default.SetPointSize(guisettings.font_default.GetPointSize() - 1)
        guisettings.font_default.SetWeight(wx.NORMAL)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(wx.Button(self, 1, U_("Idag"), size=(60, -1)), 0)
        buttons.Add(wx.Button(self, 2, "<-", size=(30, -1)), 0, wx.LEFT|wx.RIGHT, 10)
        buttons.Add(self.weeklabel, 0, wx.TOP, 5)
        buttons.Add(wx.Button(self, 3, "->", size=(30, -1)), 0, wx.LEFT|wx.RIGHT, 10)
        buttons.Add(self.datelabel, 0, wx.TOP, 5)

        wx.EVT_BUTTON(self, 1, self.GoToday)
        wx.EVT_BUTTON(self, 2, self.GoPrevWeek)
        wx.EVT_BUTTON(self, 3, self.GoNextWeek)
        return buttons
    
    def AddMenu(self):
        menubar = wx.MenuBar()

        menu = wx.Menu()
        menu.Append(120, U_("&Exportera..."))
        menu.AppendSeparator()
        menu.Append(999, U_("&Avsluta"))
        menubar.Append(menu, U_("&Arkiv"))

        menu = wx.Menu()
        menu.Append(210, U_("Valj &kurser..."))
        menu.Append(220, U_("&Uppdatera schema...\tF5"))
        menu.AppendSeparator()
        menu.Append(250, U_("Valj &grupper..."))
        menu.Append(260, U_("&Namnge kurser..."))
        menubar.Append(menu, U_("&Verktyg"))

        menu = wx.Menu()
        menu.Append(310, U_("&Om..."))
        menubar.Append(menu, U_("&Hjalp"))

        wx.EVT_MENU(self, 999, self.OnClose)
        wx.EVT_MENU(self, 120, self.ExportEvents)
        wx.EVT_MENU(self, 210, self.ChooseCourses)
        wx.EVT_MENU(self, 220, self.Update)
        wx.EVT_MENU(self, 250, self.ChooseGroups)
        wx.EVT_MENU(self, 260, self.NameCourses)
        wx.EVT_MENU(self, 310, self.About)

        self.SetMenuBar(menubar)

    def OnClose(self, event):
        try:
            timetable.timetable.save()
            settings.save()
        except error.WriteError, e:
            msg = U_("Kan inte spara installningar eller schemadata till fil.\nDen kan vara skrivskyddad eller sa tillats inte programmet skriva dar.\nFilen ar: ") + e.filename
            wx.MessageDialog(self, msg, U_("Filfel"), style=wx.OK|wx.ICON_ERROR).ShowModal()

        self.Destroy()

    def GoToday(self, event):
        self.currentmonday = calendar.Date().getLastMondayOrNextIfWeekend()
        self.updateView()

    def GoPrevWeek(self, event):
        self.currentmonday -= 7
        self.updateView()

    def GoNextWeek(self, event):
        self.currentmonday += 7
        self.updateView()

    def updateView(self):
        date = calendar.Date(self.currentmonday)

        self.weeklabel.SetLabel(U_("Vecka") + " " + str(date.getWeek()))
        self.datelabel.SetLabel(date.getMonthName() + " " + str(date.getYear()))

        if timetable.timetable.isEmpty():
            statusmsg = U_("Schemat ar tomt")
        else:
            diff = calendar.Date() - timetable.timetable.updated
            statusmsg = U_("Schemat uppdaterades for") + " " + str(diff) + " " + U_("dagar sedan")
            if diff == 0:
                statusmsg = U_("Schemat har uppdaterats idag")
            elif diff == 1:
                statusmsg = U_("Schemat uppdaterades igar")

        self.statusbar.SetStatusText(statusmsg)

        for day in self.daylabels:
            weekday = date.getWeekDay()
            self.days[weekday].colorize(date)

            # Skriver ut dagens "namn" om det �r en speciell dag,
            # exempelvis helg- eller flaggdag
            if date.getSpecialName():
                day.SetLabel(date.getSpecialName())
            else:
                day.SetLabel(date.getWeekDayName() + " " + str(date.getDay()))

            self.days[weekday].Freeze()
            self.days[weekday].clear()

            for event in timetable.timetable.getEventsForDate(date):
                self.days[weekday].addEvent(event)
            self.days[weekday].Thaw()

            date += 1

    def ImportEvents(self, evt):
        pass

    def ExportEvents(self, evt):
        ExportDialog(self).ShowModal()
        self.SetFocus()

    def Update(self, evt):
        daisycourses = timetable.courselist.getAllDaisyCourseIDs()
        timeeditcourses = timetable.courselist.getAllTimeEditCourseCodes()
        
        if not daisycourses and not timeeditcourses:
            msg = U_("Du maste forst valja vilka kurser du vill uppdatera.")
            wx.MessageDialog(self, msg, U_("Inga kurser valda"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
            return
        
        try:
            if daisycourses:
                self.updateFromDaisy(daisycourses)
            if timeeditcourses:
                self.updateFromTimeEdit(timeeditcourses)
        except error.ReadError:
            msg = U_("Kunde inte lasa fran") + " " + U_("servern") + ". " + U_("Kontrollera att du har tillgang till Internet.")
            wx.MessageDialog(self, msg, U_("Serverfel"), style=wx.OK|wx.ICON_ERROR).ShowModal()
            return
        except ValueError, e:
            msg = U_("Servern returnerade ogiltig data.\nSchemat gar inte att anvanda; uppdaterar inte.")
            wx.MessageDialog(self, msg, U_("Serverfel"), style=wx.OK|wx.ICON_ERROR).ShowModal()
            return

#        msg = str(len(difference["changed"])) + " h�ndelser uppdaterades\n"
#        msg += str(len(difference["added"])) + " h�ndelser lades till\n"
#        msg += str(len(difference["removed"])) + " h�ndelser togs bort\n"
#        wx.MessageDialog(self, msg, "Rapport", style=wx.OK|wx.ICON_INFORMATION).ShowModal()

        timetable.timetable.save()
        self.updateView()        

    def updateFromTimeEdit(self, codes):
        import timeedit
        progressdialog = ProgressDialog(self, U_("Uppdaterar schema fran") + " TimeEdit", [U_("Ansluter till schema.sys.kth.se..."), U_("Hamtar dokument...")])
        progressdialog.startProgress()
        try:
            data = timeedit.Conduit(progressdialog.increaseProgress).getvCalendarData(codes)
        except:
            progressdialog.stopProgress()
            raise

        progressdialog.stopProgress()
        timetable.timetable.importData(data, "TimeEdit")

    def updateFromDaisy(self, ids):
        import daisy
        progressdialog = ProgressDialog(self, U_("Uppdaterar schema fran") + " Daisy", [U_("Ansluter till it.kth.se..."), U_("Hamtar dokument..."), U_("Genererar schema..."), U_("Hamtar genererat schema...")])
        progressdialog.startProgress()
        try:
            data = daisy.Conduit(progressdialog.increaseProgress).getvCalendarData(ids)
        except:
            progressdialog.stopProgress()
            raise
        
        progressdialog.stopProgress()
        timetable.timetable.importData(data, "Daisy")

    def NewEvent(self, evt):
        pass

    def Preferences(self, evt):
        pass

    def About(self, evt):
        AboutDialog(self).ShowModal()

    def ChooseGroups(self, evt):
        if GroupsDialog(self).ShowModal() == wx.ID_OK:
            self.updateView()
        self.SetFocus()

    def NameCourses(self, evt):
        if CourseNamesDialog(self).ShowModal() == wx.ID_OK:
            self.updateView()
        self.SetFocus()

    def ChooseCourses(self, evt):
        if ChooseCoursesDialog(self).ShowModal() == wx.ID_OK:
            self.updateView()
            msg = U_("Vill du uppdatera schemat nu?")
            dialog = wx.MessageDialog(self, msg, U_("Uppdatera?"), style=wx.YES_NO|wx.ICON_QUESTION)
            if dialog.ShowModal() == wx.ID_YES:
                self.Update(None)
        self.SetFocus()

# -----------------------------------------------------------
class OKCancelDialog(wx.Dialog):
    "Dialogruta med OK- och Avbryt-knappar"

    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, -1, caption)

        self.cancelled = False
        self.shown = False
        self.parent = parent
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)

        self.okbtn = wx.Button(self, wx.OK, U_("&OK"))
        self.okbtn.SetDefault()

        self.buttons.Add(self.okbtn)
        self.buttons.Add((10, 0), 0)
        self.buttons.Add(wx.Button(self, wx.CANCEL, U_("&Avbryt")))

        wx.EVT_BUTTON(self, wx.OK, self.SaveAndClose)
        wx.EVT_BUTTON(self, wx.CANCEL, self.Cancel)

    def SaveAndClose(self, evt):
        print "Varning! Ingen data sparas (\"abstrakt\" metod)."
        self.EndModal(wx.ID_OK)

    def Cancel(self, evt):
        """
            Kan anropas under __init__() och d� kan dialogrutan
            inte st�ngas eftersom den inte �ppnats �n...
        """

        self.cancelled = True
        if self.shown:
            self.EndModal(wx.ID_CANCEL)

    def ShowModal(self):
        "Visar dialogrutan endast om __init__() inte avbr�ts"

        if not self.cancelled:
            self.shown = True
            return wx.Dialog.ShowModal(self)
        else:
            return wx.ID_CANCEL

# -----------------------------------------------------------
class GroupsDialog(OKCancelDialog):
    "Dialogruta f�r val av gruppdeltagande i kurser"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Valj grupper"))

        self.choices = []
        self.nogroup = U_("alla")
        self.courses = timetable.courselist.getAllDaisyCourses()
        if not self.courses:
            msg = U_("Det finns inga Daisy-kurser att valja grupp for.")
            wx.MessageDialog(self, msg, U_("Inga kurser"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
            self.Cancel(None)
            return

        allcourses = wx.BoxSizer(wx.VERTICAL)
        coursestext = wx.BoxSizer(wx.HORIZONTAL)
        centeredtext = wx.BoxSizer(wx.VERTICAL)
        layout = wx.BoxSizer(wx.VERTICAL)

        for course in self.courses:
            selectedgroup = course.group

            try:
                groups = timetable.timetable.getAllGroups(course.code)
            except ValueError:
                groups = []
                msg = U_("Det finns ingen information om vilka grupper") + " " + course.name + "\n" + U_("ar indelad i. Du maste uppdatera fran Daisy.")
                wx.MessageDialog(self, msg, U_("Gruppinformation saknas"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()

            text = StaticText(self, course.name, size=(100, -1), style=wx.ST_NO_AUTORESIZE)

            if groups:
                groups.sort()
                groups.append(self.nogroup.encode("latin_1"))
                rightcomponent = Choice(self, (70, -1), groups, course.code)

                if selectedgroup:
                    # s�tter det val som tidigare gjorts
                    rightcomponent.SetSelection(selectedgroup - 1)
                else:
                    # s�tter "ingen" som vald
                    rightcomponent.SetStringSelection(self.nogroup)
                    
                self.choices.append(rightcomponent)
            else:
                rightcomponent = StaticText(self, U_("(inget val mojligt)"))

            coursesizer = wx.BoxSizer(wx.HORIZONTAL)
            coursesizer.Add(text, 0, wx.RIGHT, 10)
            coursesizer.Add(rightcomponent)
            allcourses.Add(coursesizer, 0, wx.ALL, 10)

        noticetext = U_("Observera att de\ngruppval du gor har inte\naterspeglas i Daisy.\n\nDu kommer alltsa inte\nanmalas till nagon grupp\nautomatiskt utan maste\ngora det manuellt (precis\nsom forut).")

        centeredtext.Add((0, 10), 1)
        centeredtext.Add(StaticText(self, noticetext), 0, wx.ALL, 10)
        centeredtext.Add((0, 10), 1)

        coursestext.Add(allcourses, 0, wx.ALL, 10)
        coursestext.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL), 0, wx.EXPAND)
        coursestext.Add(centeredtext, 0, wx.ALL|wx.EXPAND, 10)

        #self.buttons.Prepend((20, 0), 1)
        #self.buttons.Prepend(wx.Button(self, 1, "&Gissa b�sta kombination"))

        layout.Add(coursestext)
        layout.Add(self.buttons, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizerAndFit(layout)
        self.Centre()

    def SaveAndClose(self, evt):
        for course in self.choices:
            if course.GetStringSelection() == self.nogroup:
                timetable.courselist.setCourseGroup(course.coursecode, 0)
            else:
                timetable.courselist.setCourseGroup(course.coursecode, course.GetSelection() + 1)

        self.EndModal(wx.ID_OK)

# -----------------------------------------------------------
class CourseNamesDialog(OKCancelDialog):
    "Dialogruta f�r egen namngivning av kurser"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Valj namn pa kurser"))

        self.coursecodes = []
        self.edits = []

        courses = timetable.courselist.courses
        if not courses:
            msg = U_("Det finns inga kurser att namnge. Valj nya kurser.")
            wx.MessageDialog(self, msg, U_("Inga kurser"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
            self.Cancel(None)
            return

        layout = wx.BoxSizer(wx.VERTICAL)

        for course in courses:
            self.coursecodes.append(course.code)

            text = StaticText(self, course.code, size=(100, -1), style=wx.ST_NO_AUTORESIZE)
            edit = wx.TextCtrl(self, -1, size=(200, -1))
            edit.SetValue(course.name)
            self.edits.append(edit)

            coursesizer = wx.BoxSizer(wx.HORIZONTAL)
            coursesizer.Add(text, 0, wx.RIGHT|wx.TOP, 7)
            coursesizer.Add(edit, 0, wx.TOP|wx.BOTTOM, 5)
            layout.Add(coursesizer, 0, wx.LEFT|wx.RIGHT, 10)

        self.buttons.Prepend((20, 0), 1)
        layout.Add(self.buttons, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizerAndFit(layout)
        self.Centre()

    def SaveAndClose(self, evt):
        for i in range(len(self.coursecodes)):
            code = self.coursecodes[i]
            name = self.edits[i].GetValue()

            if not name:
                msg = U_("Du har angett en tom strang. Programmet kommer da anvanda\nkursbeteckningen som kursnamn.")
                dialog = wx.MessageDialog(self, msg, U_("Inget namn"), style=wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
                if dialog.ShowModal() == wx.ID_OK:
                    timetable.courselist.setCourseName(code, code)
                else:
                    self.edits[i].SetFocus()
                    return
            else:
                timetable.courselist.setCourseName(code, name)

        self.EndModal(wx.ID_OK)

# -----------------------------------------------------------
class ChooseCoursesDialog(wx.Dialog):
    "Dialogruta f�r val av kurser"
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, U_("Valj schemasystem"))

        layout = wx.BoxSizer(wx.VERTICAL)
        daisy = wx.BoxSizer(wx.HORIZONTAL)
        timeedit = wx.BoxSizer(wx.HORIZONTAL)
    
        daisy.Add(wx.Button(self, 10, "&Daisy"), 0, wx.RIGHT, 10)
        daisy.Add(StaticText(self, U_("Daisy har scheman for de flesta kurser pa IT-universitetet.")), 0, wx.TOP, 5)

        timeedit.Add(wx.Button(self, 20, "&TimeEdit"), 0, wx.RIGHT, 10)
        timeedit.Add(StaticText(self, U_("TimeEdit har scheman for de flesta ovriga kurser pa KTH.")), 0, wx.TOP, 5)

        layout.Add(daisy, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
        layout.Add(timeedit, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
        layout.Add(wx.Button(self, wx.OK, U_("&Stang")), 0, wx.ALL, 10)

        wx.EVT_BUTTON(self, 10, self.ShowITUDialog)
        wx.EVT_BUTTON(self, 20, self.ShowKTHDialog)
        wx.EVT_BUTTON(self, wx.OK, self.Close)

        self.SetSizerAndFit(layout)
        self.CentreOnScreen()
        
    def Close(self, evt):
        self.EndModal(wx.ID_CANCEL)

    def ShowKTHDialog(self, evt):
        kth_dialog = ChooseKTHCoursesDialog(self)
        if kth_dialog.ShowModal() == wx.ID_CANCEL:
            self.EndModal(wx.ID_CANCEL)
            return
            
        timetable.courselist.clearTimeEditCourses()
        for course in kth_dialog.chosencourses:
            timetable.courselist.addCourse(course)

        timetable.timetable.save()
        self.EndModal(wx.ID_OK)

    def ShowITUDialog(self, evt):
        itu_dialog = ChooseITUCoursesDialog(self)
        if itu_dialog.ShowModal() == wx.ID_CANCEL:
            self.EndModal(wx.ID_CANCEL)
            return
        
        timetable.courselist.clearDaisyCourses()
        for course in itu_dialog.chosencourses:
            timetable.courselist.addCourse(course)

        timetable.timetable.save()
        self.EndModal(wx.ID_OK)

# -----------------------------------------------------------
class ChooseKTHCoursesDialog(OKCancelDialog):
    "Dialogruta f�r val av KTH-centralt-kurser"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Valj kurser"))

        layout = wx.BoxSizer(wx.VERTICAL)
        newcourse = wx.BoxSizer(wx.HORIZONTAL)
        list = wx.BoxSizer(wx.HORIZONTAL)

        self.courseedit = wx.TextCtrl(self, -1, size=(200, -1))
        addbtn = wx.Button(self, 10, U_("&Lagg till"))
        addbtn.SetDefault()
        newcourse.Add(self.courseedit, 0)
        newcourse.Add(addbtn, 0, wx.LEFT, 10)

        self.chosencourses = []
        self.courselist = wx.ListBox(self, -1, size=(200,100))
        list.Add(self.courselist)
        list.Add(wx.Button(self, 20, U_("&Ta bort")), 0, wx.LEFT, 10)
    
        wx.EVT_BUTTON(self, 10, self.AddCourse)
        wx.EVT_BUTTON(self, 20, self.RemoveCourse)
        
        layout.Add(StaticText(self, U_("Ange kurskod for en kurs i taget:")), 0, wx.LEFT|wx.TOP, 10)
        layout.Add(newcourse, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        layout.Add(list, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        layout.Add(self.buttons, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizerAndFit(layout)
        self.CentreOnScreen()
        
        timeeditcoursecodes = timetable.courselist.getAllTimeEditCourseCodes()
        timeeditcourses = []
        for code in timeeditcoursecodes:
            timeeditcourses.append(timetable.courselist.getCourse(code))

        self.addCoursesToListBox(timeeditcourses)
        
    def addCoursesToListBox(self, courses):
        for course in courses:
            self.courselist.Append(course.code + " (" + course.name + ")", course)

    def AddCourse(self, evt):
        import timeedit
        
        progressdialog = ProgressDialog(self, U_("Hamtar kursnamn"), [U_("Hamtar dokument fran schema.sys.kth.se...")])
        progressdialog.startProgress()

        try:
            course = timeedit.Conduit().getCourseInfo(self.courseedit.GetValue())
        except ValueError:
            progressdialog.stopProgress()
            msg = U_("Kursen") + " " + U_("finns inte") + " " + U_("i TimeEdits system.")
            wx.MessageDialog(self, msg, U_("Kursen") + " " + U_("finns inte"), style=wx.ICON_WARNING).ShowModal()
            self.courseedit.SetFocus()
            self.courseedit.SetSelection(-1, -1)
            return
        
        self.courselist.Append(course.code + " (" + course.name + ")", course)
        progressdialog.stopProgress()
        self.courseedit.SetFocus()
        self.courseedit.SetValue("")
        
    def RemoveCourse(self, evt):
        selected = self.courselist.GetSelections()
        for i in selected:
            self.courselist.Delete(i)
    
    def SaveAndClose(self, evt):
        self.chosencourses = []
        for i in range(self.courselist.GetCount()):
            course = self.courselist.GetClientData(i)
            self.chosencourses.append(course)
        
        self.EndModal(wx.ID_OK)
    

cachedcourselist = [] # den fr�n Internet h�mtade kurslistan cachas
# -----------------------------------------------------------
class ChooseITUCoursesDialog(OKCancelDialog):
    "Dialogruta f�r val av ITU-kurser"

    def __init__(self, parent):
        global cachedcourselist

        OKCancelDialog.__init__(self, parent, U_("Valj kurser"))
        
        self.progressdialog = ProgressDialog(self, U_("Hamtar kurslista"), [U_("Ansluter till it.kth.se..."),
            U_("Hamtar dokument..."), U_("Analyserar dokument...")])

        self.chosencourses = []
        daisycoursecodes = timetable.courselist.getAllDaisyCourseCodes()
        daisycourses = []
        for code in daisycoursecodes:
            daisycourses.append(timetable.courselist.getCourse(code))
        
        self.list_chosen = CourseListBox(self, daisycourses, id=100)
        self.list_all = CourseListBox(self, cachedcourselist, id=200, antagonist=self.list_chosen)
        
        vertbuttons = wx.BoxSizer(wx.VERTICAL)
        vertbuttons.Add((0, 10), 1)
        vertbuttons.Add(wx.Button(self, 10, "<-", size=(25,-1)))
        vertbuttons.Add((0, 10))
        vertbuttons.Add(wx.Button(self, 20, "->", size=(25,-1)))
        vertbuttons.Add((0, 10), 1)

        self.buttons.Prepend((10, 0), 1)
        self.buttons.Add((30, 0))
        self.buttons.Add(wx.Button(self, 1, U_("Hamta kurslista")))
        self.buttons.Add((10, 0), 1)

        layout = wx.BoxSizer(wx.VERTICAL)
        lists = wx.BoxSizer(wx.HORIZONTAL)

        lists.Add(self.list_chosen, 0, wx.ALL, 10)
        lists.Add(vertbuttons, 0, wx.EXPAND)
        lists.Add(self.list_all, 0, wx.ALL, 10)

        layout.Add(StaticText(self, U_("Valj de kurser vars schema ska uppdateras fran Daisy: (Ovriga kurser kommer raderas fran ditt schema.)")), 0, wx.TOP|wx.LEFT, 10)
        layout.Add(lists, 0, wx.EXPAND|wx.ALL, 10)
        layout.Add(self.buttons, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizerAndFit(layout)
        self.Centre()

        wx.EVT_BUTTON(self, 1, self.UpdateList)
        wx.EVT_BUTTON(self, 10, self.MoveLeft)
        wx.EVT_BUTTON(self, 20, self.MoveRight)
        
        wx.EVT_LISTBOX_DCLICK(self, 100, self.MoveRight)
        wx.EVT_LISTBOX_DCLICK(self, 200, self.MoveLeft)

    def UpdateList(self, evt):
        self.list_all.Set(self.getCourses())

    def MoveLeft(self, evt):
        courses = self.list_all.GetSelectedCourses()
        self.list_all.DeleteSelected()
        self.list_chosen.InsertItems(courses)

    def MoveRight(self, evt):
        courses = self.list_chosen.GetSelectedCourses()
        self.list_chosen.DeleteSelected()
        self.list_all.InsertItems(courses)

    def getCourses(self):
        import internet
        global cachedcourselist
        self.progressdialog.startProgress()

        courses = []
        try:
            courses = internet.getITUCourses(callback=self.progressdialog.increaseProgress)
            cachedcourselist = courses
        except error.ReadError:
            msg = U_("Kan inte lasa fran IT-universitetets webbplats.\nKontrollera att du har tillgang till Internet.")
            wx.MessageDialog(self, msg, U_("Internetfel"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
        except error.DataError:
            msg = U_("Fick felaktig data fran IT-universitetets kurslista.") + "\n" + U_("Det kan bero pa ett serverfel.")
            wx.MessageDialog(self, msg, U_("Datafel"), style=wx.OK|wx.ICON_ERROR).ShowModal()

        self.progressdialog.stopProgress()
        return courses

    def SaveAndClose(self, evt):
        self.chosencourses = self.list_chosen.GetAllCourses()
        self.EndModal(wx.ID_OK)

# -----------------------------------------------------------
class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        global applicationname
        global applicationversion
        wx.Dialog.__init__(self, parent, -1, U_("Om") + " " + applicationname)
        
        btn = wx.Button(self, wx.OK, U_("&Stang"))
        btn.SetDefault()
        wx.EVT_BUTTON(self, wx.OK, self.Close)

        msg = applicationname + " " + U_("ar skapat av") + u" Christian Dav�n.\n"
        msg += U_("Version") + ": " + applicationversion + "\n\n"
        msg += U_("Programmet och dess kallkod har gjorts tillganglig enligt GNU General Public License. Inga garantier for programmets funktion ges.\n\nRapportera garna buggar och funktionalitetsforslag till") + " <cd@kth.se>."

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(StaticText(self, msg, wordwrap=True, size=(250,150), style=wx.ST_NO_AUTORESIZE),
            0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        layout.Add(btn, 0, wx.ALL, 10)
        self.SetSizerAndFit(layout)
        self.Centre()
        
    def Close(self, evt):
        self.EndModal(wx.ID_OK)

# -----------------------------------------------------------
class ExportDialog(OKCancelDialog):
    "Dialogruta f�r export av schema"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Exportera schema"))

        self.fromdate = DateText(self)
        self.fromdate.setDate(parent.currentmonday)
        self.todate = DateText(self)
        self.todate.setDate(self.fromdate.date + 6)

        size = (20,20)
        # st�rre knappar i GTK �n i Windows
        if wx.Platform == "__WXGTK__":
            size = (35,30)

        fromdate = wx.BoxSizer(wx.HORIZONTAL)
        fromdate.Add(self.fromdate)
        fromdate.Add(wx.Button(self, 10, "-", size=size), 0, wx.LEFT, 10)
        fromdate.Add(wx.Button(self, 20, "+", size=size), 0, wx.LEFT, 2)
        fromdate.Add(wx.Button(self, 30, "+7", size=size), 0, wx.LEFT, 2)

        todate = wx.BoxSizer(wx.HORIZONTAL)
        todate.Add(self.todate)
        todate.Add(wx.Button(self, 110, "-", size=size), 0, wx.LEFT, 10)
        todate.Add(wx.Button(self, 120, "+", size=size), 0, wx.LEFT, 2)
        todate.Add(wx.Button(self, 130, "+7", size=size), 0, wx.LEFT, 2)

        self.buttons.Prepend((10,0), 1)
        self.buttons.Add((10,0), 1)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(StaticText(self, U_("Valj startdatum") + " " + U_("for exportering:")), 0, wx.TOP|wx.LEFT, 10)
        layout.Add(fromdate, 0, wx.ALL, 10)
        layout.Add(StaticText(self, U_("Valj slutdatum") + " " + U_("for exportering:")), 0, wx.LEFT, 10)
        layout.Add(todate, 0, wx.ALL, 10)
        layout.Add(self.buttons, 0, wx.EXPAND|wx.ALL, 10)
        self.SetSizerAndFit(layout)
        self.Centre()

        wx.EVT_BUTTON(self, 10, self.fromdate.sub)
        wx.EVT_BUTTON(self, 20, self.AddFrom)
        wx.EVT_BUTTON(self, 30, self.Add7From)
        wx.EVT_BUTTON(self, 110, self.SubTo)
        wx.EVT_BUTTON(self, 120, self.todate.add)
        wx.EVT_BUTTON(self, 130, self.Add7To)
        
    def AddFrom(self, evt):
        self.fromdate.add()
        if self.fromdate.date > self.todate.date:
            self.todate.add()
        
    def Add7From(self, evt):
        self.fromdate.add(days=7)
        if self.fromdate.date > self.todate.date:
            self.todate.add(days=7)

    def SubTo(self, evt):
        self.todate.sub()
        if self.todate.date < self.fromdate.date:
            self.fromdate.sub()
            
    def Add7To(self, evt):
        self.todate.add(days=7)

    def SaveAndClose(self, evt):
        filedialog = wx.FileDialog(self, U_("Exportera till fil"),
            wildcard=U_("vCalendar-filer") + " (*.vcs)|*.vcs|" + U_("iCalendar-filer") + " (*.ics)|*.ics|" + U_("HTML-filer") + " (*.html)|*.html|" + U_("CSV-filer") + " (*.csv)|*.csv|" + U_("Alla filer") + "|*.*",
            style=wx.SAVE|wx.OVERWRITE_PROMPT)
        if filedialog.ShowModal() == wx.ID_OK:
            import os.path
            extension = os.path.splitext(filedialog.GetPath())[1]
            
            try:
                if extension == ".ics" or extension == ".vcs":
                    self.exportVCalendar(filedialog.GetPath(), self.fromdate.date, self.todate.date)
                elif extension == ".html" or extension == ".htm":
                    self.exportHTML(filedialog.GetPath(), self.fromdate.date, self.todate.date)
                elif extension == ".csv":
                    self.exportCSV(filedialog.GetPath(), self.fromdate.date, self.todate.date)
                else:
                    msg = U_("Kan inte exportera till det angivna formatet.")
                    wx.MessageDialog(self, msg, U_("Okand filandelse"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
                    return
            except error.WriteError:
                msg = U_("Kan inte skriva till filen. Den kan vara skrivskyddad.")
                wx.MessageDialog(self, msg, U_("Filfel"), style=wx.OK|wx.ICON_WARNING).ShowModal()
                return
            
            self.EndModal(wx.ID_OK)

    def exportVCalendar(self, filename, fromdate, todate):
        timetable.VCalendarExporter().export(filename, timetable.timetable, fromdate, todate)
        
    def exportHTML(self, filename, fromdate, todate):
        timetable.HTMLExporter().export(filename, timetable.timetable, fromdate, todate)

    def exportCSV(self, filename, fromdate, todate):
        timetable.CSVExporter().export(filename, timetable.timetable, fromdate, todate)

# -----------------------------------------------------------
class DateText(wx.TextCtrl):
    "Datumtext"
    
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, size=(170, -1), style=wx.TE_READONLY)
        self.date = calendar.Date()
        self.update()

    def setDate(self, date):
        self.date = date
        self.update()

    def add(self, evt=None, days=1):
        self.date += days
        self.update()

    def sub(self, evt=None, days=1):
        self.date -= days
        self.update()
    
    def update(self):
        self.SetValue(self.date.getNiceString().lower())

# -----------------------------------------------------------
class Panel(wx.Panel):
    "Funktioner f�r alla paneler"

    def getYDelta(self, window):
        import math
        (windowsizex, windowsizey) = window.GetClientSizeTuple()
        return (windowsizex, windowsizey, math.floor(windowsizey / (settings.dayend - settings.daybegin)) + 1)

# -----------------------------------------------------------
class ProgressDialog:

    def __init__(self, parent, caption, messages=[]):
        self.progressdialog = None
        self.progress = 0
        self.parent = parent
        self.caption = caption
        self.messages = messages
    
    def setMessages(self, messages):
        self.messages = messages
    
    def startProgress(self):
        self.progress = 0
        self.progressdialog = wx.ProgressDialog(self.caption, self.messages[0],
            maximum=len(self.messages) + 1, parent=self.parent)
    
    def increaseProgress(self):
        self.progress += 1
        self.progressdialog.Update(self.progress, self.messages[self.progress])
        self.progressdialog.UpdateWindowUI()
        self.parent.UpdateWindowUI()

    def stopProgress(self):
        self.progressdialog.Destroy()

# -----------------------------------------------------------
class Choice(wx.Choice):
    def __init__(self, parent, size, choices, coursecode):
        wx.Choice.__init__(self, parent, -1, size=size, choices=choices)
        self.coursecode = coursecode

# -----------------------------------------------------------
class CourseListBox(wx.ListBox):
    "Listbox specialanpassad f�r 'dubbel kurslista'"
    
    def __init__(self, parent, courses, id=-1, antagonist=None, size=(250,300), style=0):
        wx.ListBox.__init__(self, parent, id, size=size, style=wx.LB_EXTENDED|wx.LB_SORT|style)
        self.antagonist = antagonist # ev. en annan listbox; f�r inte inneh�lla samma kurser som antagonisten
        self.Set(courses)

    def makeReadable(self, course):
        return course.name + " (" + course.code + ")"

    def Set(self, courses):
        self.Freeze()
        self.Clear()
        self.InsertItems(courses)
        self.Thaw()
        
    def __add(self, courses):
        self.Freeze()

        for course in courses:
            string = self.makeReadable(course)
            if self.FindString(string) == wx.NOT_FOUND:
                self.Append(string, course)
        
        self.Thaw()

    def InsertItems(self, courses):
        # l�gger bara till de element som inte
        # finns i den eventuella antagonisten;
        # dubletter godk�nns inte heller

        if not self.antagonist:
            self.__add(courses)
            return

        allowedlist = []
        forbiddenlist = self.antagonist.GetAllCourses()
        for course in courses:
            allowed = True

            for forbidden in forbiddenlist:
                if course == forbidden:
                    allowed = False
                    break

            if allowed:
                allowedlist.append(course)

        self.__add(allowedlist)

    def DeleteSelected(self):
        self.Freeze()
        courses = self.GetSelectedCourses()

        for course in courses:
            index = self.FindString(self.makeReadable(course))
            self.Delete(index)

        self.Thaw()

    def GetSelectedCourses(self):
        courses = []
        selected = self.GetSelections()
        for i in selected:
            courses.append(self.GetClientData(i))

        return courses

    def GetAllCourses(self):
        courses = []
        for i in range(self.GetCount()):
            courses.append(self.GetClientData(i))
            
        return courses

# -----------------------------------------------------------
class StaticText(wx.StaticText):
    "Textruta med standardtypsnitt"

    def __init__(self, parent, label, pos = (-1,-1), size = (-1,-1), wordwrap = False, style = 0):
        label = label.replace("&", "&&")        
        wx.StaticText.__init__(self, parent, -1, label, pos=pos, size=size, style=style)
        self.SetFont(guisettings.font_default)

        self.wordwrap = False
        self.originallabel = ""

        # "Wordwrap" finns endast p� wxGTK med st�d f�r GTK2
        if wx.Platform == "__WXGTK__" and wordwrap:
            self.wordwrap = True
            self.originallabel = label
            self.SetLabel(self.wordWrap(label))

        wx.EVT_SIZE(self, self.OnResize)
        
    def OnResize(self, evt):
        if self.wordwrap:
            self.SetLabel(self.wordWrap(self.originallabel))
        
    def getOneWord(self, text):
        separators = " -,"
        word = ""
        for i in range(len(text)):
            if text[i] in separators:
                word = text[:i+1]
                text = text[i+1:]
                break
        
        if not word:
            word = text
            text = ""

        return (word, text)

    def wrapLine(self, line):
        (maxwidth,y) = self.GetClientSizeTuple()
        lines = [""]
        
        while line:
            (word, line) = self.getOneWord(line)            
            temp = lines[-1] + word
            if self.GetTextExtent(temp)[0] > maxwidth and lines[-1]:
                lines[-1] += "\n"
                lines.append(word)
            else:
                lines[-1] += word

        linestring = ""
        for line in lines:
            linestring += line

        return linestring
        
    def wordWrap(self, label):
        lines = label.splitlines()
        label = ""
        for line in lines:
            if label: label += "\n"
            label += self.wrapLine(line)
        
        return label       


# -----------------------------------------------------------
class TimePanel(Panel):
    def __init__(self, parent):
        import sys
        style = wx.SIMPLE_BORDER
        if wx.MINOR_VERSION >= 5:
            style |= wx.FULL_REPAINT_ON_RESIZE

        Panel.__init__(self, parent, -1, size=(60,250), style=style)
        wx.EVT_PAINT(self, self.OnPaint)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        self.drawLines(dc)

    def drawLines(self, dc):
        (windowsizex, windowsizey, ydelta) = self.getYDelta(self)

        dc.SetPen(wx.Pen(guisettings.colour_lines, 1, style=wx.DOT))

        lasty = 0
        for hour in range(settings.daybegin.getHour() + 1, settings.dayend.getHour()):
            y = int(lasty + ydelta)
            lasty = y

            # vissa versioner/plattformar har olika varianter av denna funktion
            try:
                dc.DrawLine(wx.Point(0, y), wx.Point(windowsizex, y))
            except TypeError:
                dc.DrawLine(0, y, windowsizex, y)

# -----------------------------------------------------------
class HoursPanel(TimePanel):

    def __init__(self, parent):
        self.hours = []

        TimePanel.__init__(self, parent)
        self.SetBackgroundColour(guisettings.bgcolour_hours)
        if wx.MINOR_VERSION >= 5:
            self.ClearBackground()

    def OnPaint(self, evt):
        """
            Skriver ut timangivelserna bredvid schemat.

            I GTK utl�ses OnPaint varje g�ng vi skriver ut
            dessa, varf�r det blir en o�ndlig loop. F�r att
            undvika det ritas timmarna bara ut om hela
            panelen har �ndrats och beh�ver ritas om.
        """

        if wx.Platform == "__WXGTK__":
            (panelwidth, panelheight) = self.GetClientSizeTuple()
            (a, b, sizex, sizey) = self.GetUpdateRegion().GetBox()
            if sizex != panelwidth or sizey != panelheight:
                return

        self.printHours()
        TimePanel.OnPaint(self, evt)

    def printHours(self):
        (windowsizex, windowsizey, ydelta) = self.getYDelta(self)

        while True:
            try:
                h = self.hours.pop()
            except IndexError:
                break

            h.Destroy()

        lasty = -ydelta + 1
        for hour in range(settings.daybegin.getHour(), settings.dayend.getHour()):
            y = lasty + ydelta
            lasty = y
            h = StaticText(self, str(hour) + ":00", pos=(10, y))
            h.SetFont(guisettings.font_default)
            self.hours.append(h)

# -----------------------------------------------------------
class EventOrganiser:
    "Ordnar h�ndelser -- f�rberedande f�r den grafiska utplaceringen"

    def __init__(self):
        self.events = []

    def clear(self):
        self.events = []

    def fitsInColumn(self, column, event):
        # j�mf�r med varje h�ndelse i aktuell kolumn
        for columnevent in column:
            if self.isClash(columnevent, event):
                return False
            
        return True
    
    def countClashes(self, columns):
        for event in self.events:
            for c in columns:
                for columnevent in c:
                    if columnevent is event:
                        continue

                    # en kollision i en kolumn
                    if self.isClash(columnevent, event):
                        event.clashes += 1
                        break

        self.setMaxClashes()

    def setMaxClashes(self):
        """
            S�tter alla h�ndelsers antal kollisioner till det h�gsta v�rdet
            bland h�ndelserna i "kollisionsgruppen"
        """
        already = []
        for event in self.events:
            if event in already:
                continue

            clashes = []
            self.getClashGroup(event, clashes)
            already.extend(clashes)

            # ingen "kollisionsgrupp", dvs. en h�ndelse som inte kolliderar
            if not clashes:
                continue

            maxclashes = 0
            for clash in clashes:
                maxclashes = max(clash.clashes, maxclashes)
                
            for clash in clashes:
                clash.clashes = maxclashes
                
    def showAllEvents(self):
        # den rena superklassen kan inte visa n�gon grafik,
        # d�remot subklassen DayPanel
        if self.__class__ == EventOrganiser:
            return

        for event in self.events:
            event.show()

    def addEvent(self, event):
        self.events.append(GraphicalEvent(self, event))

        columns = [[]]

        for event in self.events:
            event.clashes = 0
            foundspot = False

            columnno = 0
            # tittar igenom alla kolumner
            for c in columns:
                # om ej kollision i denna kolumn, addera h�ndelse
                if self.fitsInColumn(c, event):
                    event.column = columnno
                    c.append(event)
                    foundspot = True
                    break

                columnno += 1
                    
            if not foundspot:
                event.column = len(columns)
                columns.append([event])

        self.countClashes(columns)
        self.showAllEvents()

    def isClash(self, event1, event2):
        if event1 == event2:
            return False
    
        if (event1.begin <= event2.begin and event1.end > event2.begin) or \
        (event2.begin <= event1.begin and event2.end > event1.begin):
            return True
        else:
            return False

    def getClashGroup(self, event, clashes):
        """
            Fyller 'clashes' med alla h�ndelser som kolliderar "i grupp",
            exempelvis 9-11, 10-14 och 11-13. Anv�nds f�r att kunna avg�ra
            hur mycket (visuell) plats varje h�ndelse kan uppta i schemat.
        """

        for other in self.events:
            if other is event or other in clashes:
                continue

            if self.isClash(event, other):
                clashes.append(other)
                self.getClashGroup(other, clashes)

# -----------------------------------------------------------
class DayPanel(TimePanel, EventOrganiser):
    "Panel f�r en dag, med h�ndelser"

    def __init__(self, parent):
        TimePanel.__init__(self, parent)
        EventOrganiser.__init__(self)
        wx.EVT_SIZE(self, self.OnResize)

    def OnResize(self, evt):
        "Ritar om alla visade h�ndelser"

        for event in self.events:
            event.redraw()
            
    def clear(self):
        for event in self.events:
            event.hide()

        EventOrganiser.clear(self)

    def colorize(self, today):
        if calendar.Date() == today:
            self.SetBackgroundColour(guisettings.bgcolour_schedule_today)
        elif today.isHoliday():
            self.SetBackgroundColour(guisettings.bgcolour_schedule_holiday)
        else:
            self.SetBackgroundColour(guisettings.bgcolour_schedule)

        # ritar om bakgrunden samt linjerna
        self.Refresh()

# -----------------------------------------------------------
class GraphicalEvent(timetable.Event):
    "H�ndelse som �ven inneh�ller information om det grafiska"

    def __init__(self, parent, event):
        timetable.Event.__init__(self)
        self.parent = parent
        self.panel = None
        self.clashes = 0
        self.column = 0
        self.copy(event)

    def show(self):
        if self.panel:
            self.panel.Destroy()

        self.panel = EventPanel(self.parent, self, self.clashes, self.column)

    def hide(self):
        if self.panel:
            self.panel.Destroy()

    def redraw(self):
        if self.panel:
            self.panel.resize()

# -----------------------------------------------------------
class EventPanel(Panel):
    "En h�ndelse visualiserad som en panel"

    def __init__(self, parent, event, clashes, column):
        self.parent = parent
        self.event = event
        self.clashes = clashes
        self.column = column
        self.label = None
        
        (sizex, sizey) = self.calcSize()
        (posx, posy) = self.calcPos(sizex)
        
        Panel.__init__(self, parent, -1, size=(sizex, sizey), pos=(posx, posy), style=wx.SIMPLE_BORDER)
        self.paint()

        wx.EVT_LEFT_DCLICK(self.label, self.OnClick)
        self.SetToolTip(wx.ToolTip(self.event.getNiceString()))

    def calcSize(self):
        import math
        (windowsizex, windowsizey, ydelta) = self.getYDelta(self.parent)
        sizex = windowsizex / (self.clashes + 1) + 1
        sizey = math.floor((self.event.end - self.event.begin) * ydelta)
        return (sizex, sizey)

    def calcPos(self, sizex):
        import math
        (windowsizex, windowsizey, ydelta) = self.getYDelta(self.parent)
        posx = (sizex - 1) * self.column
        posy = math.floor((self.event.begin - settings.daybegin) * ydelta)
        return (posx, posy)

    def resize(self):
        (sizex, sizey) = self.calcSize()
        (posx, posy) = self.calcPos(sizex)
        self.SetSize((sizex, sizey))
        self.MoveXY(posx, posy)
        self.label.SetSize((sizex - 3, sizey - 3))
        
    def paint(self):
        bgcolour = guisettings.bgcolour_event
        fgcolour = guisettings.colour_event_text
        
        if self.event.type in settings.eventtype_examination:
            bgcolour = guisettings.bgcolour_event_examination
        elif not self.event.active:
            bgcolour = guisettings.bgcolour_event_inactive
            fgcolour = guisettings.colour_event_inactive

        self.SetBackgroundColour(bgcolour)
        self.SetForegroundColour(fgcolour)
        if self.label:
            self.label.SetForegroundColour(fgcolour)
            self.label.SetBackgroundColour(bgcolour)

        if wx.MINOR_VERSION >= 5:
            self.ClearBackground()

        self.label = StaticText(self, unicode(self.event), wordwrap=True, pos=(2,2), style=wx.ST_NO_AUTORESIZE)
        self.resize()

    def OnClick(self, evt):
        timetable.timetable.getEvent(self.event.getID()).toggleActive()
        self.event.toggleActive()
        self.SetToolTip(wx.ToolTip(self.event.getNiceString()))
        self.paint()

