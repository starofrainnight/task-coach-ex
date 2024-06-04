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

""" These are unittests of wxPython functionality. Of course, the goal is
not to test all wxPython functions, but rather to document platform
inconsistencies or surprising behaviour. """  # pylint: disable=W0105

import wx
import test
from taskcoachlib import operating_system


class TextCtrlTest(test.wxTestCase):
    def testClearEmitsNoEventOnMacOSX(self):
        self.clearTextCausesEvent = False  # pylint: disable=W0201
        textCtrl = wx.TextCtrl(self.frame)
        textCtrl.Bind(wx.EVT_TEXT, self.onTextChanged)
        textCtrl.Clear()
        if operating_system.isMac():  # pragma: no cover
            self.assertFalse(self.clearTextCausesEvent)
        else:  # pragma: no cover
            self.assertTrue(self.clearTextCausesEvent)

    def onTextChanged(self, event):  # pylint: disable=W0613
        self.clearTextCausesEvent = (
            True  # pragma: no cover pylint: disable=W0201
        )
