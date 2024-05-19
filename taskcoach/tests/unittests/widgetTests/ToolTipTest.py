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

import test, wx
from taskcoachlib.widgets import tooltip


class ToolTipUnderTest(
    tooltip.ToolTipMixin, wx.Frame
):  # pylint: disable=W0223
    def GetMainWindow(self):
        return self


class DummyToolTipWindow(object):
    def __init__(self, size=(10, 10)):
        self.size = size
        self.rect = None

    def Show(self, *args):
        self.rect = args

    def GetSize(self):
        return self.size


class ToolTipMixinTestCase(test.TestCase):
    def setUp(self):
        self.tooltipMixin = ToolTipUnderTest(None)

    def testShowTip(self):
        tipWindow = DummyToolTipWindow()
        self.tooltipMixin.DoShowTip(0, 0, tipWindow)
        self.assertEqual((0, 0, 10, 10), tipWindow.rect)

    def testReallyBigTip(self):
        width, height = wx.ClientDisplayRect()[2:]
        tipWindow = DummyToolTipWindow((2 * width, 2 * height))
        self.tooltipMixin.DoShowTip(0, 0, tipWindow)
        self.assertEqual((5, 5, 2 * width, height - 10), tipWindow.rect)

    def testTipThatFallsOfBottomOfScreen(self):
        _, displayY, _, height = wx.ClientDisplayRect()
        tipWindow = DummyToolTipWindow((10, 100))
        self.tooltipMixin.DoShowTip(0, height - 10, tipWindow)
        self.assertEqual((0, height - 105 + displayY, 10, 100), tipWindow.rect)


class SimpleToolTipUnderTest(tooltip.SimpleToolTip):
    def _calculateLineSize(self, dc, line):
        """Make sure the unittest doesn't depend on the platform font size."""
        return 10, 20


class SimpleToolTipTestCase(test.wxTestCase):
    def setUp(self):
        self.tip = SimpleToolTipUnderTest(self.frame)

    def testOneShortLine(self):
        self.tip.SetData([(None, ["First line"])])
        self.assertEqual([(None, ["First line"])], self.tip.data)

    def testOneLongLine(self):
        self.tip.SetData([(None, ["First line " * 10])])
        self.assertEqual(
            [
                (
                    None,
                    [("First line " * 7).strip(), ("First line " * 3).strip()],
                )
            ],
            self.tip.data,
        )

    def testCalculateSize(self):
        self.tip.SetData([(None, ["First line"])])
        self.assertEqual(wx.Size(16, 27), self.tip._calculateSize())
