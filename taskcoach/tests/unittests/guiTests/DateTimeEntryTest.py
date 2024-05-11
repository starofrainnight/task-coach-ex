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
from taskcoachlib.gui.dialog import entry
from taskcoachlib.domain import date
from taskcoachlib import config


class DateTimeEntryTest(test.wxTestCase):
    def setUp(self):
        super(DateTimeEntryTest, self).setUp()
        self.dateTimeEntry = entry.DateTimeEntry(
            self.frame, config.Settings(load=False)
        )
        self.dateTime = date.DateTime(2004, 1, 1)

    def testCreate(self):
        self.assertEqual(date.DateTime(), self.dateTimeEntry.GetValue())

    def testSet(self):
        now = date.Now()
        self.dateTimeEntry.SetValue(now)
        self.assertAlmostEqual(
            now.toordinal(),
            self.dateTimeEntry.GetValue().toordinal(),
            places=2,
        )

    def testReset(self):
        self.dateTimeEntry.SetValue()
        self.assertEqual(date.DateTime(), self.dateTimeEntry.GetValue())

    def testValidDateTime(self):
        self.dateTimeEntry.SetValue(self.dateTime)
        self.assertEqual(self.dateTime, self.dateTimeEntry.GetValue())


class DateEntryConstructorTest(test.wxTestCase):
    def testCreateWithDate(self):
        tomorrow = date.Tomorrow()
        dateTimeEntry = entry.DateTimeEntry(
            self.frame, config.Settings(load=False), tomorrow
        )
        self.assertAlmostEqual(
            tomorrow.toordinal(),
            dateTimeEntry.GetValue().toordinal(),
            places=2,
        )


class TimeDeltaEntryTest(test.wxTestCase):
    def setUp(self):
        super(TimeDeltaEntryTest, self).setUp()
        self.timeDeltaEntry = entry.TimeDeltaEntry(self.frame)

    def testDefaultValue(self):
        self.assertEqual(date.TimeDelta(), self.timeDeltaEntry.GetValue())

    def testDefaultDisplayedValue(self):
        self.assertEqual(
            "        0:00:00", self.timeDeltaEntry._entry.GetValue()
        )

    def testSetValue(self):
        self.timeDeltaEntry.SetValue(date.TimeDelta(hours=10, seconds=5))
        self.assertEqual(
            "       10:00:05", self.timeDeltaEntry._entry.GetValue()
        )

    def testOverflow(self):
        self.timeDeltaEntry.SetValue(date.TimeDelta(hours=12345678912))
        self.assertEqual(
            "123456789:00:00", self.timeDeltaEntry._entry.GetValue()
        )


class ReadOnlyTimeDeltaEntryTest(test.wxTestCase):
    def setUp(self):
        super(ReadOnlyTimeDeltaEntryTest, self).setUp()
        self.timeDeltaEntry = entry.TimeDeltaEntry(self.frame, readonly=True)

    def testSetNegativeValue(self):
        self.timeDeltaEntry.SetValue(date.TimeDelta(hours=-10, minutes=-20))
        self.assertEqual(
            "      -10:20:00", self.timeDeltaEntry._entry.GetValue()
        )

    def testSetSmallNegativeValue(self):
        self.timeDeltaEntry.SetValue(date.TimeDelta(seconds=-4))
        self.assertEqual(
            "       -0:00:04", self.timeDeltaEntry._entry.GetValue()
        )
