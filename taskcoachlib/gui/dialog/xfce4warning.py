"""
Task Coach - Your friendly task manager
Copyright (C) 2012 Task Coach developers <developers@taskcoach.org>

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

import wx
from taskcoachlib.i18n import _
from taskcoachlib.widgets import dialog


class XFCE4WarningDialog(dialog.Dialog):
    def __init__(self, parent, settings):
        self.__settings = settings
        super(XFCE4WarningDialog, self).__init__(
            parent, _("Warning"), buttonTypes=wx.OK
        )

    def createInterior(self):
        return wx.Panel(self._panel)

    def fillInterior(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(
            wx.StaticText(
                self._interior,
                label=_(
                    "Task Coach has known issues with XFCE4 session management.\n"
                )
                + _(
                    'If you experience random freeze at startup, please uncheck\nthe "Use X11 session management" in the Features tab of the preferences.\n'
                ),
            )
        )
        self._checkbox = wx.CheckBox(
            self._interior, label=_("Do not show this dialog at startup")
        )  # pylint: disable=W0201
        self._checkbox.SetValue(True)
        sizer.Add(self._checkbox)
        self._interior.SetSizer(sizer)

    def ok(self, event=None):
        self.__settings.setboolean(
            "feature", "showsmwarning", not self._checkbox.GetValue()
        )
        super(XFCE4WarningDialog, self).ok(event)
