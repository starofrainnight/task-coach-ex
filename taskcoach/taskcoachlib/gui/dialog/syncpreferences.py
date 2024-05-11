# -*- coding: utf-8 -*-

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

import wx
from taskcoachlib.gui.dialog.preferences import SettingsPageBase
from taskcoachlib import widgets, operating_system
from taskcoachlib.i18n import _


class SyncMLBasePage(SettingsPageBase):
    def __init__(self, iocontroller=None, *args, **kwargs):
        super(SyncMLBasePage, self).__init__(*args, **kwargs)

        self.iocontroller = iocontroller
        self.config = iocontroller.syncMLConfig()

    def get(self, section, name):
        if section == "access":
            if name in ["syncUrl"]:
                return str(
                    self.config.children()[0]["spds"]["syncml"]["Conn"].get(
                        name
                    )
                )
            elif name in ["username"]:
                return str(
                    self.config.children()[0]["spds"]["syncml"]["Auth"].get(
                        name
                    )
                )

        elif section == "task":
            for child in self.config.children()[0]["spds"][
                "sources"
            ].children():
                if child.name.endswith("Tasks"):
                    return child.get(name)

        elif section == "note":
            for child in self.config.children()[0]["spds"][
                "sources"
            ].children():
                if child.name.endswith("Notes"):
                    return child.get(name)
        return ""

    def set(self, section, name, value):
        if section == "access":
            if name in ["syncUrl"]:
                self.config.children()[0]["spds"]["syncml"]["Conn"].set(
                    name, value
                )
            elif name in ["username"]:
                self.config.children()[0]["spds"]["syncml"]["Auth"].set(
                    name, value
                )

        elif section == "task":
            for child in self.config.children()[0]["spds"][
                "sources"
            ].children():
                if child.name.endswith("Tasks"):
                    child.set(name, value)
                    break

        elif section == "note":
            for child in self.config.children()[0]["spds"][
                "sources"
            ].children():
                if child.name.endswith("Notes"):
                    child.set(name, value)
                    break

    def ok(self):
        super(SyncMLBasePage, self).ok()

        self.iocontroller.setSyncMLConfig(self.config)


class SyncMLAccessPage(SyncMLBasePage):
    def __init__(self, *args, **kwargs):
        super(SyncMLAccessPage, self).__init__(*args, **kwargs)

        choice = self.addChoiceSetting(
            None,
            "preset",
            _("SyncML server"),
            "",
            [
                ("0", _("Custom")),
                ("1", _("MemoToo (http://www.memotoo.com/)")),
                ("2", _("Horde-based")),
            ],
        )[0]
        wx.EVT_CHOICE(choice, wx.ID_ANY, self.OnPresetChanged)

        self.addTextSetting("access", "syncUrl", _("SyncML server URL"))
        self.addTextSetting("access", "username", _("User name/ID"))

        checkBox = self.addBooleanSetting(
            "task", "dosync", _("Enable tasks synchronization")
        )
        wx.EVT_CHECKBOX(checkBox, wx.ID_ANY, self.OnSyncTaskChanged)
        self.addTextSetting("task", "uri", _("Tasks database name"))
        self.addChoiceSetting(
            "task",
            "preferredsyncmode",
            _("Preferred synchronization mode"),
            "",
            [
                ("TWO_WAY", _("Two way")),
                ("SLOW", _("Slow")),
                ("ONE_WAY_FROM_CLIENT", _("One way from client")),
                ("REFRESH_FROM_CLIENT", _("Refresh from client")),
                ("ONE_WAY_FROM_SERVER", _("One way from server")),
                ("REFRESH_FROM_SERVER", _("Refresh from server")),
            ],
        )
        self.enableTextSetting(
            "task", "uri", self.getboolean("task", "dosync")
        )
        self.enableChoiceSetting(
            "task", "preferredsyncmode", self.getboolean("task", "dosync")
        )

        checkBox = self.addBooleanSetting(
            "note", "dosync", _("Enable notes synchronization")
        )
        wx.EVT_CHECKBOX(checkBox, wx.ID_ANY, self.OnSyncNoteChanged)
        self.addTextSetting("note", "uri", _("Notes database name"))
        self.addChoiceSetting(
            "note",
            "preferredsyncmode",
            _("Preferred synchronization mode"),
            "",
            [
                ("TWO_WAY", _("Two way")),
                ("SLOW", _("Slow")),
                ("ONE_WAY_FROM_CLIENT", _("One way from client")),
                ("REFRESH_FROM_CLIENT", _("Refresh from client")),
                ("ONE_WAY_FROM_SERVER", _("One way from server")),
                ("REFRESH_FROM_SERVER", _("Refresh from server")),
            ],
        )
        self.enableTextSetting(
            "note", "uri", self.getboolean("note", "dosync")
        )
        self.enableChoiceSetting(
            "note", "preferredsyncmode", self.getboolean("note", "dosync")
        )

        self.fit()

    def OnPresetChanged(self, event):
        if event.GetInt() == 1:
            self.setTextSetting(
                "access", "syncUrl", "http://sync.memotoo.com/syncml"
            )
            self.setTextSetting("task", "uri", "task")
            self.setTextSetting("note", "uri", "note")
        elif event.GetInt() == 2:
            self.setTextSetting(
                "access", "syncUrl", "http://<hostname_and_path>/rpc.php"
            )
            self.setTextSetting("task", "uri", "tasks")
            self.setTextSetting("note", "uri", "notes")

    def OnSyncTaskChanged(self, event):
        self.enableTextSetting("task", "uri", event.IsChecked())
        self.enableChoiceSetting(
            "task", "preferredsyncmode", event.IsChecked()
        )

    def OnSyncNoteChanged(self, event):
        self.enableTextSetting("note", "uri", event.IsChecked())
        self.enableChoiceSetting(
            "note", "preferredsyncmode", event.IsChecked()
        )


class SyncMLPreferences(widgets.NotebookDialog):
    def __init__(self, iocontroller=None, *args, **kwargs):
        self.iocontroller = iocontroller
        super(SyncMLPreferences, self).__init__(
            bitmap="wrench_icon", *args, **kwargs
        )
        self.SetSize((700, -1))
        if operating_system.isMac():
            self.CentreOnParent()

    def addPages(self):
        self._interior.SetMinSize((550, 400))
        kwargs = dict(
            parent=self._interior, columns=3, iocontroller=self.iocontroller
        )
        # pylint: disable=W0142
        pages = [
            (
                SyncMLAccessPage(growableColumn=1, **kwargs),
                _("Access"),
                "earth_blue_icon",
            )
        ]

        for page, title, bitmap in pages:
            self._interior.AddPage(page, title, bitmap=bitmap)
