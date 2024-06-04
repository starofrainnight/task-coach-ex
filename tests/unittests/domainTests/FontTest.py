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
from taskcoachlib.domain.attribute import font


class MixFontsTest(test.TestCase):
    def setUp(self):
        super(MixFontsTest, self).setUp()
        self.mixFonts = font.FontMixer.mix
        self.font = wx.Font(
            10,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        self.lightFont = wx.Font(
            self.font.GetPointSize(),
            self.font.GetFamily(),
            self.font.GetStyle(),
            wx.FONTWEIGHT_LIGHT,
        )
        self.boldFont = wx.Font(
            self.font.GetPointSize(),
            self.font.GetFamily(),
            self.font.GetStyle(),
            wx.FONTWEIGHT_BOLD,
        )
        self.italicFont = wx.Font(
            self.font.GetPointSize(),
            self.font.GetFamily(),
            wx.FONTSTYLE_ITALIC,
            self.font.GetWeight(),
        )
        self.underlinedFont = wx.Font(
            self.font.GetPointSize(),
            self.font.GetFamily(),
            self.font.GetStyle(),
            self.font.GetWeight(),
            underline=True,
        )
        self.swissFont = wx.Font(
            self.font.GetPointSize(),
            wx.FONTFAMILY_SWISS,
            self.font.GetStyle(),
            self.font.GetWeight(),
        )
        self.decorativeFont = wx.Font(
            self.font.GetPointSize(),
            wx.FONTFAMILY_DECORATIVE,
            self.font.GetStyle(),
            self.font.GetWeight(),
        )
        self.romanFont = wx.Font(
            self.font.GetPointSize(),
            wx.FONTFAMILY_ROMAN,
            self.font.GetStyle(),
            self.font.GetWeight(),
        )
        self.scriptFont = wx.Font(
            self.font.GetPointSize(),
            wx.FONTFAMILY_SCRIPT,
            self.font.GetStyle(),
            self.font.GetWeight(),
        )
        self.modernFont = wx.Font(
            self.font.GetPointSize(),
            wx.FONTFAMILY_MODERN,
            self.font.GetStyle(),
            self.font.GetWeight(),
        )
        self.teletypeFont = wx.Font(
            self.font.GetPointSize(),
            wx.FONTFAMILY_TELETYPE,
            self.font.GetStyle(),
            self.font.GetWeight(),
        )

    def testOneFont(self):
        self.assertEqual(self.font, self.mixFonts(self.font))

    def testFontSize(self):
        biggerFont = wx.Font(
            self.font.GetPointSize() + 2,
            self.font.GetFamily(),
            self.font.GetStyle(),
            self.font.GetWeight(),
        )
        expectedFontSize = (
            biggerFont.GetPointSize() + self.font.GetPointSize()
        ) / 2
        self.assertEqual(
            expectedFontSize,
            self.mixFonts(self.font, biggerFont).GetPointSize(),
        )

    def testFontWeight_NormalAndBold(self):
        self.assertEqual(
            wx.FONTWEIGHT_BOLD,
            self.mixFonts(self.font, self.boldFont).GetWeight(),
        )

    def testFontWeight_NormalAndLight(self):
        self.assertEqual(
            wx.FONTWEIGHT_LIGHT,
            self.mixFonts(self.font, self.lightFont).GetWeight(),
        )

    def testFontWeight_LightAndBold(self):
        self.assertEqual(
            wx.FONTWEIGHT_NORMAL,
            self.mixFonts(self.boldFont, self.lightFont).GetWeight(),
        )

    def testFontWeight_TwoLightAndOneBold(self):
        self.assertEqual(
            wx.FONTWEIGHT_LIGHT,
            self.mixFonts(
                self.boldFont, self.lightFont, self.lightFont
            ).GetWeight(),
        )

    def testFontStyle_NormalAndItalic(self):
        self.assertEqual(
            wx.FONTSTYLE_ITALIC,
            self.mixFonts(self.font, self.italicFont).GetStyle(),
        )

    def testFontUnderline_NormalAndUnderlined(self):
        self.assertTrue(
            self.mixFonts(self.font, self.underlinedFont).GetUnderlined()
        )

    def testFontFamily_DefaultAndSwiss(self):
        self.assertEqual(
            wx.FONTFAMILY_SWISS,
            self.mixFonts(self.font, self.swissFont).GetFamily(),
        )

    @test.skipOnPlatform("__WXGTK__")
    def testFontFamily_DefaultAndDecorative(self):
        self.assertEqual(
            wx.FONTFAMILY_DECORATIVE,
            self.mixFonts(self.font, self.decorativeFont).GetFamily(),
        )

    def testFontFamily_DefaultAndRoman(self):
        self.assertEqual(
            wx.FONTFAMILY_ROMAN,
            self.mixFonts(
                self.font, self.romanFont, self.romanFont
            ).GetFamily(),
        )

    @test.skipOnPlatform("__WXGTK__")
    def testFontFamily_DefaultAndScript(self):
        self.assertEqual(
            wx.FONTFAMILY_SCRIPT,
            self.mixFonts(self.font, self.scriptFont).GetFamily(),
        )

    @test.skipOnPlatform("__WXGTK__")
    def testFontFamily_DefaultAndModern(self):
        self.assertEqual(
            wx.FONTFAMILY_MODERN,
            self.mixFonts(self.font, self.modernFont).GetFamily(),
        )

    def testFontFamily_DefaultAndTeletype(self):
        self.assertEqual(
            wx.FONTFAMILY_TELETYPE,
            self.mixFonts(
                self.font, self.teletypeFont, self.teletypeFont
            ).GetFamily(),
        )

    def testFontFamily_RomandAndSwissAndTwoTeletype(self):
        self.assertEqual(
            wx.FONTFAMILY_TELETYPE,
            self.mixFonts(
                self.romanFont,
                self.teletypeFont,
                self.swissFont,
                self.teletypeFont,
            ).GetFamily(),
        )
