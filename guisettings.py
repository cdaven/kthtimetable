# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

import wx
import sys

colour_lines = wx.Colour(128, 128, 128)
colour_event_text = wx.Colour(0, 0, 0)
colour_event_inactive = wx.Colour(128, 128, 128)

bgcolour_default = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DLIGHT)
bgcolour_daylabel = wx.Colour(255, 255, 255)
bgcolour_schedule = wx.Colour(192, 192, 192)
bgcolour_schedule_today = wx.Colour(255, 255, 255)
bgcolour_hours = wx.Colour(255, 255, 204)
bgcolour_event = wx.Colour(51, 153, 255)
bgcolour_event_examination = wx.Colour(255, 51, 51)
bgcolour_event_personal = wx.Colour(204, 255, 204)
bgcolour_event_inactive = wx.Colour(204, 204, 204)

if sys.platform == "win32":
    font_default = wx.SystemSettings_GetFont(wx.SYS_ICONTITLE_FONT)
else:
    font_default = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
