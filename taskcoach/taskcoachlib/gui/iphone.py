"""
Task Coach - Your friendly task manager
Copyright (C) 2004-2016 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from taskcoachlib.notify import NotificationFrameBase, NotificationCenter
from taskcoachlib.i18n import _
import wx


class IPhoneSyncFrame(NotificationFrameBase):
    def __init__(self, settings, *args, **kwargs):
        self.settings = settings

        super(IPhoneSyncFrame, self).__init__(*args, **kwargs)

    def AddInnerContent(self, sizer, panel):
        self.text = wx.StaticText(panel, wx.ID_ANY, _("Synchronizing..."))
        sizer.Add(self.text, 0, wx.ALL, 3)

        self.gauge = wx.Gauge(panel, wx.ID_ANY)
        self.gauge.SetRange(100)
        sizer.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 3)

        if self.settings.getboolean("iphone", "showlog"):
            self.log = wx.TextCtrl(
                panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY
            )
            sizer.Add(self.log, 1, wx.EXPAND | wx.ALL, 3)

            self.btn = wx.Button(panel, wx.ID_ANY, _("OK"))
            sizer.Add(self.btn, 0, wx.ALIGN_CENTRE | wx.ALL, 3)
            self.btn.Enable(False)
            wx.EVT_BUTTON(self.btn, wx.ID_ANY, self.OnOK)

    def CloseButton(self, panel):
        return None

    def SetDeviceName(self, name):
        self.text.SetLabel(_("Synchronizing with %s...") % name)

    def SetProgress(self, value, total):
        self.gauge.SetValue(int(100 * value / total))

    def AddLogLine(self, line):
        if self.settings.getboolean("iphone", "showlog"):
            self.log.AppendText(line + "\n")

    def Started(self):
        NotificationCenter().NotifyFrame(self)

    def Finished(self):
        if self.settings.getboolean("iphone", "showlog"):
            self.btn.Enable(True)
        else:
            self.DoClose()

    def OnOK(self, event):
        self.DoClose()
