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

import test, locale
from taskcoachlib import widgets, render
from taskcoachlib.domain import date


class CommonTestsMixin(object):
    def setUp(self):
        super(CommonTestsMixin, self).setUp()
        # LC_ALL does not work on Slackware or Arch, but LC_TIME crashes on Fedora...
        try:
            self.__oldLocale = locale.getlocale(locale.LC_ALL)
            self.__localeDomain = locale.LC_ALL
        except TypeError:
            self.__oldLocale = locale.getlocale(locale.LC_TIME)
            self.__localeDomain = locale.LC_TIME
        localeName = "en_US" if self.ampm else "fr_FR"
        # OS X and Linux don't agree on encoding names...
        for encodingName in ["utf8", "UTF-8"]:
            try:
                locale.setlocale(
                    self.__localeDomain, "%s.%s" % (localeName, encodingName)
                )
            except locale.Error:
                pass
            else:
                break
        else:
            self.skipTest(
                'No supported locale found. Try "locale -a" and add a supported locale.'
            )
        reload(render)  # To execute module-level code every time

    def tearDown(self):
        locale.setlocale(self.__localeDomain, self.__oldLocale)
        reload(render)
        super(CommonTestsMixin, self).tearDown()

    def _format(self, hour, minute, second):
        if self.ampm:
            dpyHour = hour % 12
            if dpyHour == 0:
                dpyHour = 12
            r = "%02d:%02d" % (dpyHour, minute)
            if self.showSeconds:
                r += ":%02d" % second
            r += " AM" if hour <= 12 else " PM"
        else:
            r = "%02d:%02d" % (hour, minute)
            if self.showSeconds:
                r += ":%02d" % second
        return r

    def testGetValue(self):
        oneHour = date.DateTime(2000, 1, 1, hour=1)
        self.dateTimeCtrl.SetValue(oneHour)
        self.assertEqual(oneHour, self.dateTimeCtrl.GetValue())


class DateTimeCtrlTestCase(test.wxTestCase):
    adjustEndOfDay = False
    showSeconds = False

    def setUp(self):
        super(DateTimeCtrlTestCase, self).setUp()
        self.dateTimeCtrl = widgets.datectrl.DateTimeCtrl(
            self.frame,
            showSeconds=self.showSeconds,
            adjustEndOfDay=self.adjustEndOfDay,
        )

    def test_adjust(self):
        self.dateTimeCtrl.SetValue(date.DateTime(2012, 12, 12, 23, 59, 0, 0))
        self.assertEqual(
            self.dateTimeCtrl.GetValue(),
            (
                date.DateTime(2012, 12, 12, 23, 59, 59, 999999)
                if self.adjustEndOfDay
                else date.DateTime(2012, 12, 12, 23, 59, 0, 0)
            ),
        )


class DateTimeCtrlTest_Seconds_Base(CommonTestsMixin):
    showSeconds = True

    def testGetValue_SecondPrecision(self):
        oneHourAndTenSeconds = date.DateTime(2000, 1, 1, hour=1, second=10)
        self.dateTimeCtrl.SetValue(oneHourAndTenSeconds)
        self.assertEqual(oneHourAndTenSeconds, self.dateTimeCtrl.GetValue())


class DateTimeCtrlTest_Seconds(
    DateTimeCtrlTest_Seconds_Base, DateTimeCtrlTestCase
):
    ampm = False


class DateTimeCtrlTest_Seconds_AMPM(
    DateTimeCtrlTest_Seconds_Base, DateTimeCtrlTestCase
):
    ampm = True


class DateTimeCtrlTest_NoSeconds_Base(CommonTestsMixin):
    showSeconds = False

    def testGetValue_SecondPrecision(self):
        oneHour = date.DateTime(2000, 1, 1, hour=1)
        oneHourAndTenSeconds = date.DateTime(2000, 1, 1, hour=1, second=10)
        self.dateTimeCtrl.SetValue(oneHourAndTenSeconds)
        self.assertEqual(oneHour, self.dateTimeCtrl.GetValue())


class DateTimeCtrlTest_NoSeconds(
    DateTimeCtrlTest_NoSeconds_Base, DateTimeCtrlTestCase
):
    ampm = False


class DateTimeCtrlTest_NoSeconds_Adjust(
    DateTimeCtrlTest_NoSeconds_Base, DateTimeCtrlTestCase
):
    ampm = False
    adjustEndOfDay = True


class DateTimeCtrlTest_NoSeconds_AMPM(
    DateTimeCtrlTest_NoSeconds_Base, DateTimeCtrlTestCase
):
    ampm = True


class DateTimeCtrlTest_NoSeconds_AMPM_Adjust(
    DateTimeCtrlTest_NoSeconds_Base, DateTimeCtrlTestCase
):
    ampm = True
    adjustEndOfDay = True
