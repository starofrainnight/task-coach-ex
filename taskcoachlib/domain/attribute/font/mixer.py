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


class FontMixer(object):
    @classmethod
    def mix(class_, *fonts):
        fonts = [font for font in fonts if font]
        if not fonts:
            return None
        elif len(fonts) == 1:
            return fonts[0]
        pointSize = class_.mixFontSizes(*fonts)
        family = class_.mixFontFamilies(*fonts)
        weight = class_.mixFontWeights(*fonts)
        style = class_.mixFontStyles(*fonts)
        underlined = class_.mixFontUnderlining(*fonts)
        return wx.Font(pointSize, family, style, weight, underline=underlined)

    @staticmethod
    def mixFontSizes(*fonts):
        size = 0
        for font in fonts:
            size += font.GetPointSize()
        return size / len(fonts)

    allFamilies = (
        wx.FONTFAMILY_SWISS,
        wx.FONTFAMILY_DECORATIVE,
        wx.FONTFAMILY_ROMAN,
        wx.FONTFAMILY_SCRIPT,
        wx.FONTFAMILY_MODERN,
        wx.FONTFAMILY_TELETYPE,
    )

    @classmethod
    def mixFontFamilies(class_, *fonts):
        families = [font.GetFamily() for font in fonts]
        counts = dict()
        for family in class_.allFamilies:
            counts[family] = families.count(family)
        for family in class_.allFamilies:
            countsCopy = counts.copy()
            familyCount = countsCopy.pop(family)
            if familyCount > max(countsCopy.values()):
                return family
        return wx.FONTFAMILY_DEFAULT

    @staticmethod
    def mixFontWeights(*fonts):
        weights = [font.GetWeight() for font in fonts]
        countLight = weights.count(wx.FONTWEIGHT_LIGHT)
        countBold = weights.count(wx.FONTWEIGHT_BOLD)
        if countBold > countLight:
            return wx.FONTWEIGHT_BOLD
        if countLight > countBold:
            return wx.FONTWEIGHT_LIGHT
        return wx.FONTWEIGHT_NORMAL

    @staticmethod
    def mixFontStyles(*fonts):
        """If any of the fonts is italic, return italic else normal. We
        ignore slant style since a font created with the
        wx.FONTSTYLE_SLANT style returns wx.FONTSTYLE_ITALIC as its
        style."""
        anyItalic = wx.FONTSTYLE_ITALIC in [font.GetStyle() for font in fonts]
        return wx.FONTSTYLE_ITALIC if anyItalic else wx.FONTSTYLE_NORMAL

    @staticmethod
    def mixFontUnderlining(*fonts):
        return any(font.GetUnderlined() for font in fonts)
