# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import wx
import settings
import guisettings
import calendar
import timetable
import error
from i18n import *

applicationname = "KTH TimeTable"
applicationversion = "2.2"

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
            msg = U_("It's been more than a week since you last fetched the timetable. It could have been\nupdated since. Would you like to fetch the timetable now?")
            if wx.MessageDialog(self, msg, U_("The timetable is old"),
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

        # ritar ut saker för varje veckodag
        for i in range(settings.lastweekday + 1):
            # själva namnet på dagen (fylls i senare under updateView())
            self.daylabels.append(StaticText(self, "Ons 15", size=(60, 15), style=wx.ST_NO_AUTORESIZE|wx.ALIGN_CENTRE|wx.SIMPLE_BORDER))
            self.daylabels[-1].SetBackgroundColour(guisettings.bgcolour_daylabel)

            daynames.Add(self.daylabels[-1], 1, wx.RIGHT|wx.LEFT, 1)

            # schemat för dagen, åtminstone utrymmet för detsamma
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
        buttons.Add(wx.Button(self, 1, U_("Today"), size=(60, -1)), 0)
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
        menu.Append(120, U_("&Export..."))
        menu.AppendSeparator()
        menu.Append(999, U_("&Quit"))
        menubar.Append(menu, U_("&File"))

        menu = wx.Menu()
        menu.Append(210, U_("Choose &courses..."))
        menu.Append(220, U_("&Fetch timetable...\tF5"))
        menu.AppendSeparator()
        menu.Append(250, U_("Choose &groups..."))
        menu.Append(260, U_("&Name courses..."))
        menu.AppendSeparator()
        menu.Append(270, U_("&Settings..."))
        menubar.Append(menu, U_("&Tools"))

        menu = wx.Menu()
        menu.Append(310, U_("&About..."))
        menubar.Append(menu, U_("&Help"))

        wx.EVT_MENU(self, 999, self.OnClose)
        wx.EVT_MENU(self, 120, self.ExportEvents)
        wx.EVT_MENU(self, 210, self.ChooseCourses)
        wx.EVT_MENU(self, 220, self.Update)
        wx.EVT_MENU(self, 250, self.ChooseGroups)
        wx.EVT_MENU(self, 260, self.NameCourses)
        wx.EVT_MENU(self, 270, self.MakeSettings)
        wx.EVT_MENU(self, 310, self.About)

        self.SetMenuBar(menubar)

    def OnClose(self, event):
        try:
            timetable.timetable.save()
        except error.WriteError, e:
            msg = U_("Could not save the timetable. The file may be write-protected. The filename is") + ": " + e.filename
            wx.MessageDialog(self, msg, U_("File error"), style=wx.OK|wx.ICON_ERROR).ShowModal()

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

        self.weeklabel.SetLabel(U_("Week") + " " + str(date.getWeek()))
        self.datelabel.SetLabel(date.getMonthName() + " " + str(date.getYear()))

        if timetable.timetable.isEmpty():
            statusmsg = U_("The timetable is empty")
        else:
            diff = calendar.Date() - timetable.timetable.updated
            statusmsg = U_("The timetable was fetched") + " " + str(diff) + " " + U_("days ago")
            if diff == 0:
                statusmsg = U_("The timetable was fetched") + " " + U_("today")
            elif diff == 1:
                statusmsg = U_("The timetable was fetched") + " " + U_("yesterday")

        self.statusbar.SetStatusText(statusmsg)

        for day in self.daylabels:
            weekday = date.getWeekDay()
            self.days[weekday].colorize(date)

            # Skriver ut dagens "namn" om det är en speciell dag,
            # exempelvis helg- eller flaggdag
            if date.getSpecialName():
                day.SetLabel(date.getSpecialName())
            else:
                day.SetLabel(date.getWeekDayName() + " " + str(date.getDay()))

            self.days[weekday].Freeze()
            self.days[weekday].clear()

            for event in timetable.timetable.getEventsForDate(date):
                self.days[weekday].addEvent(event)

            self.days[weekday].showEvents()
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
            msg = U_("First you must choose which courses to fetch.")
            wx.MessageDialog(self, msg, U_("No courses"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
            return
        
        try:
            if daisycourses:
                self.updateFromDaisy(daisycourses)
            if timeeditcourses:
                self.updateFromTimeEdit(timeeditcourses)
        except error.ReadError:
            msg = U_("Could not read from") + " " + U_("the timetable server") + ". " + U_("Make sure you have access to the Internet.")
            wx.MessageDialog(self, msg, U_("Server error"), style=wx.OK|wx.ICON_ERROR).ShowModal()
            return
        except ValueError, e:
            msg = U_("The timetable fetched from the server is corrupt and unusable.")
            wx.MessageDialog(self, msg, U_("Server error"), style=wx.OK|wx.ICON_ERROR).ShowModal()
            return

#        msg = str(len(difference["changed"])) + " händelser uppdaterades\n"
#        msg += str(len(difference["added"])) + " händelser lades till\n"
#        msg += str(len(difference["removed"])) + " händelser togs bort\n"
#        wx.MessageDialog(self, msg, "Rapport", style=wx.OK|wx.ICON_INFORMATION).ShowModal()

        timetable.timetable.save()
        self.updateView()        

    def updateFromTimeEdit(self, codes):
        import timeedit
        progressdialog = ProgressDialog(self, U_("Fetching the timetable from") + " TimeEdit", [U_("Connecting to") + " schema.sys.kth.se...", U_("Receiving timetable...")])
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
        progressdialog = ProgressDialog(self, U_("Fetching the timetable from") + " Daisy", [U_("Connecting to") + " it.kth.se...", U_("Receiving data..."), U_("Generating timetable..."), U_("Receiving timetable...")])
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
            msg = U_("Do you want to fetch the timetable now?")
            dialog = wx.MessageDialog(self, msg, U_("Fetch timetable?"), style=wx.YES_NO|wx.ICON_QUESTION)
            if dialog.ShowModal() == wx.ID_YES:
                self.Update(None)
        self.SetFocus()

    def MakeSettings(self, evt):
        if SettingsDialog(self).ShowModal() == wx.ID_OK:
            self.updateView()
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
        self.buttons.Add(wx.Button(self, wx.CANCEL, U_("&Cancel")))

        wx.EVT_BUTTON(self, wx.OK, self.SaveAndClose)
        wx.EVT_BUTTON(self, wx.CANCEL, self.Cancel)

    def SaveAndClose(self, evt):
        print "Varning! Ingen data sparas (\"abstrakt\" metod)."
        self.EndModal(wx.ID_OK)

    def Cancel(self, evt):
        """
            Kan anropas under __init__() och då kan dialogrutan
            inte stängas eftersom den inte öppnats än...
        """

        self.cancelled = True
        if self.shown:
            self.EndModal(wx.ID_CANCEL)

    def ShowModal(self):
        "Visar dialogrutan endast om __init__() inte avbröts"

        if not self.cancelled:
            self.shown = True
            return wx.Dialog.ShowModal(self)
        else:
            return wx.ID_CANCEL

# -----------------------------------------------------------
class GroupsDialog(OKCancelDialog):
    "Dialogruta för val av gruppdeltagande i kurser"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Choose groups"))

        self.choices = []
        self.nogroup = U_("all")
        self.courses = timetable.courselist.getAllDaisyCourses()
        if not self.courses:
            msg = U_("There are no fetched Daisy courses.\nYou can only choose groups for Daisy courses.")
            wx.MessageDialog(self, msg, U_("No courses"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
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
                msg = U_("There is no information on which groups") + " " + course.name + "\n" + U_("is divided into. You have to fetch timetable from Daisy.")
                wx.MessageDialog(self, msg, U_("Group information missing"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()

            text = StaticText(self, course.name, size=(150, -1), style=wx.ST_NO_AUTORESIZE)

            if groups:
                groups.sort()
                groups.append(self.nogroup.encode("latin_1"))
                rightcomponent = Choice(self, (70, -1), groups, course.code)

                if selectedgroup:
                    # sätter det val som tidigare gjorts
                    rightcomponent.SetSelection(selectedgroup - 1)
                else:
                    # sätter "ingen" som vald
                    rightcomponent.SetStringSelection(self.nogroup)
                    
                self.choices.append(rightcomponent)
            else:
                rightcomponent = StaticText(self, U_("(no choice possible)"))

            coursesizer = wx.BoxSizer(wx.HORIZONTAL)
            coursesizer.Add(text, 0, wx.RIGHT, 10)
            coursesizer.Add(rightcomponent)
            allcourses.Add(coursesizer, 0, wx.ALL, 10)

        noticetext = U_("Please note that the choices you make here are not reflected\nin Daisy. You will NOT be assigned to these groups.\nYou have to choose your groups in Daisy as well.")

        centeredtext.Add((0, 10), 1)
        centeredtext.Add(StaticText(self, noticetext), 0, wx.ALL, 10)
        centeredtext.Add((0, 10), 1)

        coursestext.Add(allcourses, 0, wx.ALL, 10)
        coursestext.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL), 0, wx.EXPAND)
        coursestext.Add(centeredtext, 0, wx.ALL|wx.EXPAND, 10)

        #self.buttons.Prepend((20, 0), 1)
        #self.buttons.Prepend(wx.Button(self, 1, "&Gissa bästa kombination"))

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
    "Dialogruta för egen namngivning av kurser"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Name courses"))

        self.coursecodes = []
        self.edits = []

        courses = timetable.courselist.courses
        if not courses:
            msg = U_("There are no courses to name. Please choose some first.")
            wx.MessageDialog(self, msg, U_("No courses"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
            self.Cancel(None)
            return

        layout = wx.BoxSizer(wx.VERTICAL)

        for course in courses:
            self.coursecodes.append(course.code)

            text = StaticText(self, course.code, size=(110, -1), style=wx.ST_NO_AUTORESIZE)
            edit = wx.TextCtrl(self, -1, size=(240, -1))
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
                msg = U_("You have entered an empty string. This entry will be ignored.")
                dialog = wx.MessageDialog(self, msg, U_("Empty string ignored"), style=wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
                if dialog.ShowModal() == wx.ID_OK:
                    timetable.courselist.setCourseName(code, code)
                else:
                    self.edits[i].SetFocus()
                    return
            else:
                timetable.courselist.setCourseName(code, name)

        self.EndModal(wx.ID_OK)

# -----------------------------------------------------------
class SettingsDialog(OKCancelDialog):
    "Dialogruta för inställningar"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Change settings"))
        layout = wx.BoxSizer(wx.VERTICAL)
        setting1 = wx.BoxSizer(wx.HORIZONTAL)
        setting2 = wx.BoxSizer(wx.HORIZONTAL)
        setting3 = wx.BoxSizer(wx.HORIZONTAL)
        setting4 = wx.BoxSizer(wx.HORIZONTAL)

        size = (150,-1)

        setting1.Add(StaticText(self, U_("Days in week:"), size=size, style=wx.ST_NO_AUTORESIZE), 0, wx.ALL, 10)
        self.daysinweek = wx.Choice(self, -1, size=(70,-1), choices=["5", "6", "7"])
        self.daysinweek.SetSelection(settings.lastweekday - 4)
        setting1.Add(self.daysinweek, 0, wx.LEFT|wx.RIGHT, 10)

        setting2.Add(StaticText(self, U_("Program language:"), size=size, style=wx.ST_NO_AUTORESIZE), 0, wx.ALL, 10)
        self.language = wx.Choice(self, -1, size=(100,-1), choices=["English", "Svenska"])
        if settings.language == "en": self.language.SetSelection(0)
        elif settings.language == "sv": self.language.SetSelection(1)
        setting2.Add(self.language, 0, wx.LEFT|wx.RIGHT, 10)

        setting3.Add(StaticText(self, U_("Start of day:"), size=size, style=wx.ST_NO_AUTORESIZE), 0, wx.ALL, 10)
        self.daybegin = wx.Choice(self, -1, size=(80,-1), choices=["08:00", "09:00", "10:00"])
        if settings.daybegin <= calendar.Time("080000"): self.daybegin.SetSelection(0)
        elif settings.daybegin <= calendar.Time("090000"): self.daybegin.SetSelection(1)
        else: self.daybegin.SetSelection(2)
        setting3.Add(self.daybegin, 0, wx.LEFT|wx.RIGHT, 10)

        setting4.Add(StaticText(self, U_("End of day:"), size=size, style=wx.ST_NO_AUTORESIZE), 0, wx.ALL, 10)
        self.dayend = wx.Choice(self, -1, size=(80,-1), choices=["17:00", "18:00", "19:00", "20:00", "21:00"])
        if settings.dayend <= calendar.Time("170000"): self.dayend.SetSelection(0)
        elif settings.dayend <= calendar.Time("180000"): self.dayend.SetSelection(1)
        elif settings.dayend <= calendar.Time("190000"): self.dayend.SetSelection(2)
        elif settings.dayend <= calendar.Time("200000"): self.dayend.SetSelection(3)
        else: self.dayend.SetSelection(4)
        setting4.Add(self.dayend, 0, wx.LEFT|wx.RIGHT, 10)

        layout.Add(StaticText(self, U_("The settings will need a\nprogram restart to take effect.")), 0, wx.EXPAND|wx.ALL, 10)
        layout.Add(setting1, 0, wx.EXPAND|wx.ALL, 10)
        layout.Add(setting3, 0, wx.EXPAND|wx.ALL, 10)
        layout.Add(setting4, 0, wx.EXPAND|wx.ALL, 10)
        layout.Add(setting2, 0, wx.EXPAND|wx.ALL, 10)
        layout.Add(self.buttons, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizerAndFit(layout)
        self.CentreOnScreen()

    def SaveAndClose(self, evt):
        settings.dayend = calendar.Time(self.dayend.GetStringSelection()[:2] + "0000")
        settings.daybegin = calendar.Time(self.daybegin.GetStringSelection()[:2] + "0000")
        settings.language = self.language.GetStringSelection()[:2].lower()
        settings.lastweekday = int(self.daysinweek.GetStringSelection()) - 1

        self.EndModal(wx.ID_OK)

# -----------------------------------------------------------
class ChooseCoursesDialog(OKCancelDialog):
    "Dialogruta för val av kurser"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Choose courses"))

        layout = wx.BoxSizer(wx.VERTICAL)
        newcourse = wx.BoxSizer(wx.HORIZONTAL)
        list = wx.BoxSizer(wx.HORIZONTAL)

        self.courseedit = wx.TextCtrl(self, -1, size=(400, -1))
        addbtn = wx.Button(self, 10, U_("&Add"))
        addbtn.SetDefault()
        newcourse.Add(self.courseedit, 0)
        newcourse.Add(addbtn, 0, wx.LEFT, 10)

        self.chosencourses = []
        self.courselist = CourseListBox(self, timetable.courselist.getAllCourses(), size=(400,250))
        list.Add(self.courselist)
        list.Add(wx.Button(self, 20, U_("&Remove")), 0, wx.LEFT, 10)
    
        wx.EVT_BUTTON(self, 10, self.AddCourse)
        wx.EVT_BUTTON(self, 20, self.RemoveCourse)
        
        layout.Add(StaticText(self, U_("Choose the courses you want included in your timetable. Both TimeEdit\nand Daisy courses can be added. The course code may be incomplete\nfor Daisy courses; all matching courses will then be added.")), 0, wx.LEFT|wx.TOP, 10)
        layout.Add(StaticText(self, U_("Enter one course code at a time:")), 0, wx.LEFT|wx.TOP, 10)
        layout.Add(newcourse, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        layout.Add(list, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        layout.Add(self.buttons, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizerAndFit(layout)
        self.CentreOnScreen()
        
        self.daisycourses = timetable.CachedCourseList()
        if self.daisycourses.isEmpty():
            self.daisycourses.setCourses(self.getDaisyCourses())
            self.daisycourses.save()

    def getDaisyCourses(self):
        import daisy
        progressdialog = ProgressDialog(self, U_("Fetching course list"), [U_("Connecting to") + " it.kth.se...",
            U_("Receiving data..."), U_("Connecting to") + " it.kth.se...", U_("Receiving data..."), ""])
        progressdialog.startProgress()

        courses = []
        try:
            courses = daisy.Conduit().getCourses(progressdialog.increaseProgress)
        except error.ReadError:
            msg = U_("Could not read from") + " " + U_("the IT University web site.") + "\n" + U_("Make sure you have access to the Internet.")
            wx.MessageDialog(self, msg, U_("Server error"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
        except error.DataError:
            msg = U_("Got bad and unusable data from") + " " + U_("the IT University web site.")
            wx.MessageDialog(self, msg, U_("Server error"), style=wx.OK|wx.ICON_ERROR).ShowModal()

        progressdialog.stopProgress()
        return courses

    def AddCourse(self, evt):
        code = self.courseedit.GetValue()
        courses = self.lookForCourseInDaisy(code)
        if courses:
            # kursen fanns i Daisy, lägger till alla som matchar
            self.courselist.InsertItems(courses)
        else:
            # letar i TimeEdit istället
            self.lookForCourseInTimeEdit(code)

        self.SetFocus()
        self.courseedit.SetFocus()
        self.courseedit.SetValue("")

    def lookForCourseInDaisy(self, code):
        courses = []
        try:
            courses = self.daisycourses.getCourses(code)
        except ValueError:
            pass

        return courses

    def lookForCourseInTimeEdit(self, code):
        import timeedit
        
        progressdialog = ProgressDialog(self, U_("Fetching course name"), [U_("Receiving data from") + " schema.sys.kth.se..."])
        progressdialog.startProgress()

        try:
            course = timeedit.Conduit().getCourseInfo(code)
        except ValueError:
            progressdialog.stopProgress()
            msg = U_("The course") + " " + U_("does not exist") + " " + U_("in Daisy or TimeEdit.")
            wx.MessageDialog(self, msg, U_("The course") + " " + U_("does not exist"),
                style=wx.ICON_WARNING).ShowModal()
            return
        
        self.courselist.InsertItems([course])
        progressdialog.stopProgress()
        
    def RemoveCourse(self, evt):
        self.courselist.DeleteSelected()
    
    def SaveAndClose(self, evt):
        timetable.courselist.clear()
        for i in range(self.courselist.GetCount()):
            timetable.courselist.addCourse(self.courselist.GetClientData(i))
        timetable.timetable.removeOrphanEvents()
        self.EndModal(wx.ID_OK)


# -----------------------------------------------------------
class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        global applicationname
        global applicationversion
        wx.Dialog.__init__(self, parent, -1, U_("About") + " " + applicationname)
        
        btn = wx.Button(self, wx.OK, U_("&Close"))
        btn.SetDefault()
        wx.EVT_BUTTON(self, wx.OK, self.Close)

        msg = applicationname + " " + U_("is created by") + u" Christian Davén.\n"
        msg += U_("Version:") + " " + applicationversion + "\n\n"
        msg += U_("The program and its source code is licensed under the terms of the GNU GPL.\n\nPlease send bug reports and suggestions to") + " <cd@kth.se>"

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(StaticText(self, msg, wordwrap=True, size=(300,150), style=wx.ST_NO_AUTORESIZE),
            0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        layout.Add(btn, 0, wx.ALL, 10)
        self.SetSizerAndFit(layout)
        self.Centre()
        
    def Close(self, evt):
        self.EndModal(wx.ID_OK)

# -----------------------------------------------------------
class ExportDialog(OKCancelDialog):
    "Dialogruta för export av schema"

    def __init__(self, parent):
        OKCancelDialog.__init__(self, parent, U_("Export timetable"))

        self.fromdate = DateText(self)
        self.fromdate.setDate(parent.currentmonday)
        self.todate = DateText(self)
        self.todate.setDate(self.fromdate.date + 6)

        size = (20,20)
        # större knappar i GTK än i Windows
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
        layout.Add(StaticText(self, U_("Choose start date") + " " + U_("for export:")), 0, wx.TOP|wx.LEFT, 10)
        layout.Add(fromdate, 0, wx.ALL, 10)
        layout.Add(StaticText(self, U_("Choose end date") + " " + U_("for export:")), 0, wx.LEFT, 10)
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
        filedialog = wx.FileDialog(self, U_("Export to file"),
            wildcard=U_("vCalendar files") + " (*.vcs)|*.vcs|" + U_("iCalendar files") + " (*.ics)|*.ics|" + U_("HTML files") + " (*.html)|*.html|" + U_("CSV files") + " (*.csv)|*.csv|" + U_("All files") + "|*.*",
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
                    msg = U_("Cannot export to the chosen file format.")
                    wx.MessageDialog(self, msg, U_("Unknown extension"), style=wx.OK|wx.ICON_INFORMATION).ShowModal()
                    return
            except error.WriteError:
                msg = U_("Could not write to the file. It could be write-protected.")
                wx.MessageDialog(self, msg, U_("File error"), style=wx.OK|wx.ICON_WARNING).ShowModal()
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
    "Funktioner för alla paneler"

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
    "Listbox för kurslista; innehåller alltid högst en av varje kurs"
    
    def __init__(self, parent, courses, id=-1, size=(250,300), style=0):
        wx.ListBox.__init__(self, parent, id, size=size, style=wx.LB_EXTENDED|wx.LB_SORT|style)
        self.Set(courses)

    def Set(self, courses):
        self.Freeze()
        self.Clear()
        self.InsertItems(courses)
        self.Thaw()

    def __courseToString(self, course):
        return course.name + " (" + course.code + ")"
        
    def InsertItems(self, courses):
        self.Freeze()

        for course in courses:
            already = False
            for i in range(self.GetCount()):
                if course.code == self.GetClientData(i).code:
                    already = True

            if not already:
                self.Append(self.__courseToString(course), course)

        self.Thaw()

    def DeleteSelected(self):
        self.Freeze()
        courses = self.GetSelectedCourses()

        for course in courses:
            index = self.FindString(self.__courseToString(course))
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

        # "Wordwrap" finns endast i wxWindows och wxGTK med stöd för GTK2
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

            I GTK utlöses OnPaint varje gång vi skriver ut
            dessa, varför det blir en oändlig loop. För att
            undvika det ritas timmarna bara ut om hela
            panelen har ändrats och behöver ritas om.
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
    "Ordnar händelser -- förberedande för den grafiska utplaceringen"

    def __init__(self):
        self.events = []

    def clear(self):
        self.events = []

    def fitsInColumn(self, column, event):
        # jämför med varje händelse i aktuell kolumn
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
            Sätter alla händelsers antal kollisioner till det högsta värdet
            bland händelserna i "kollisionsgruppen"
        """
        already = []
        for event in self.events:
            if event in already:
                continue

            clashes = []
            self.getClashGroup(event, clashes)
            already.extend(clashes)

            # ingen "kollisionsgrupp", dvs. en händelse som inte kolliderar
            if not clashes:
                continue

            maxclashes = 0
            for clash in clashes:
                maxclashes = max(clash.clashes, maxclashes)
                
            for clash in clashes:
                clash.clashes = maxclashes
                
    def showEvents(self):
        # den rena superklassen kan inte visa någon grafik,
        # däremot subklassen DayPanel
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
                # om ej kollision i denna kolumn, addera händelse
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
            Fyller 'clashes' med alla händelser som kolliderar "i grupp",
            exempelvis 9-11, 10-14 och 11-13. Används för att kunna avgöra
            hur mycket (visuell) plats varje händelse kan uppta i schemat.
        """

        for other in self.events:
            if other is event or other in clashes:
                continue

            if self.isClash(event, other):
                clashes.append(other)
                self.getClashGroup(other, clashes)

# -----------------------------------------------------------
class DayPanel(TimePanel, EventOrganiser):
    "Panel för en dag, med händelser"

    def __init__(self, parent):
        TimePanel.__init__(self, parent)
        EventOrganiser.__init__(self)
        wx.EVT_SIZE(self, self.OnResize)

    def OnResize(self, evt):
        "Ritar om alla visade händelser"

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
    "Händelse som även innehåller information om det grafiska"

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
    "En händelse visualiserad som en panel"

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

