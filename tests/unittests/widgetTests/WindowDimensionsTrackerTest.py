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
import test
from taskcoachlib import gui, config, operating_system


class WindowDimensionsTrackerTest(test.wxTestCase):
    def setUp(self):
        super(WindowDimensionsTrackerTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.section = "window"
        self.settings.setvalue(self.section, "position", (50, 50))
        self.settings.setvalue(self.section, "starticonized", "Never")
        if operating_system.isWindows():
            self.frame.Show()
        self.tracker = gui.windowdimensionstracker.WindowDimensionsTracker(
            self.frame, self.settings
        )

    def test_initial_position(self):
        self.assertEqual(
            self.settings.getvalue(self.section, "position"),
            self.frame.GetPosition(),
        )

    def test_initial_size(self):
        # See MainWindowTest...
        width, height = self.frame.GetSize()
        if operating_system.isMac():  # pragma: no cover
            width, height = self.frame.GetClientSize()
            height -= 18
        self.assertEqual(
            (width, height), self.settings.getvalue(self.section, "size")
        )

    @test.skipOnPlatform("__WXGTK__")
    def test_maximize(self):
        for maximized in [True, False]:
            self.frame.Maximize(maximized)
            self.assertEqual(maximized, self.frame.IsMaximized())
            self.assertEqual(
                maximized, self.settings.getboolean(self.section, "maximized")
            )

    def test_change_size(self):
        self.frame.Maximize(False)
        if operating_system.isMac():
            self.frame.SetClientSize((123, 200))
        else:
            self.frame.ProcessEvent(wx.SizeEvent((123, 200)))
        self.assertEqual(
            (123, 200), self.settings.getvalue(self.section, "size")
        )

    def test_move(self):
        self.frame.Maximize(False)
        self.frame.Iconize(False)
        self.frame.ProcessEvent(wx.MoveEvent((200, 200)))
        self.assertEqual(
            (200, 200), self.settings.getvalue(self.section, "position")
        )
