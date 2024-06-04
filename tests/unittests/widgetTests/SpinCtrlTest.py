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

import test
from taskcoachlib import widgets


class SpinCtrlTest(test.wxTestCase):
    def testPositiveValue(self):
        spinCtrl = widgets.SpinCtrl(self.frame, value=5)
        self.assertEqual(5, spinCtrl.GetValue())

    def testNegativeValue(self):
        spinCtrl = widgets.SpinCtrl(self.frame, value=-5)
        self.assertEqual(-5, spinCtrl.GetValue())

    def testMinRange(self):
        spinCtrl = widgets.SpinCtrl(self.frame, min=1)
        self.assertEqual(1, spinCtrl.GetMin())

    def testDefaultValueIsAtLeastMinRange(self):
        spinCtrl = widgets.SpinCtrl(self.frame, min=1)
        self.assertEqual(1, spinCtrl.GetValue())

    def testMaxRange(self):
        spinCtrl = widgets.SpinCtrl(self.frame, max=100)
        self.assertEqual(100, spinCtrl.GetMax())

    def testDefaultValueIsAtMostMaxRange(self):
        spinCtrl = widgets.SpinCtrl(self.frame, max=-1)
        self.assertEqual(-1, spinCtrl.GetValue())
