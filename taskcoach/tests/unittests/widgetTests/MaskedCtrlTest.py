# -*- coding: UTF-8 -*-
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
from taskcoachlib.widgets import masked


class LocalConv(dict):
    def __init__(self, decimal_point=".", thousands_sep=",", grouping=None):
        super(LocalConv, self).__init__()
        self.update(
            dict(
                decimal_point=decimal_point,
                thousands_sep=thousands_sep,
                grouping=grouping or [],
            )
        )


class AmountCtrlTest(test.wxTestCase):
    def setUp(self):
        super(AmountCtrlTest, self).setUp()
        self.amountCtrl = masked.AmountCtrl(self.frame)

    def testCreate(self):
        self.assertEqual(0.0, self.amountCtrl.GetValue())

    def testSetValue(self):
        self.amountCtrl.SetValue(1.0)
        self.assertEqual(1.0, self.amountCtrl.GetValue())

    def testDefaultLocalConventions(self):
        masked.AmountCtrl(self.frame, locale_conventions=LocalConv())

    def testCommaAsDecimalSepAndNoGrouping(self):
        masked.AmountCtrl(
            self.frame, locale_conventions=LocalConv(decimal_point=",")
        )

    def testCommaAsDecimalSepAndGrouping(self):
        masked.AmountCtrl(
            self.frame,
            locale_conventions=LocalConv(
                decimal_point=",", grouping=[3, 3, 3]
            ),
        )

    def testCommaAsBothDecimalSepAndThousandsSepButNoGrouping(self):
        masked.AmountCtrl(
            self.frame,
            locale_conventions=LocalConv(decimal_point=",", thousands_sep=","),
        )

    def testCommaAsBothDecimalSepAndThousandsSepAndGrouping(self):
        masked.AmountCtrl(
            self.frame,
            locale_conventions=LocalConv(
                decimal_point=",", thousands_sep=",", grouping=[3, 3, 3]
            ),
        )

    def testSpaceIsNotAllowedAsDecimalPoint(self):
        try:
            masked.AmountCtrl(
                self.frame, locale_conventions=LocalConv(decimal_point=" ")
            )
            self.fail("Expected ValueError")  # pragma: no cover
        except ValueError:
            pass

    def testNonAsciiDecimalPoint(self):
        masked.AmountCtrl(
            self.frame, locale_conventions=LocalConv(decimal_point="�")
        )

    def testNonAsciiThousandsSeparator(self):
        masked.AmountCtrl(
            self.frame,
            locale_conventions=LocalConv(
                thousands_sep="�", grouping=[3, 3, 3]
            ),
        )

    def testMultiCharThousandsSeparator(self):
        masked.AmountCtrl(
            self.frame, locale_conventions=LocalConv(thousands_sep="..")
        )
