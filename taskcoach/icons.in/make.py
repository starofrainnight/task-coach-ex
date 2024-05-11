#!/usr/bin/env python

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

import sys
import os
from wx.tools import img2py


def extractIcon(iconZipFile, pngFilename, pngZipped):
    pngFile = open(pngFilename, "wb")
    pngFile.write(iconZipFile.read(pngZipped))
    pngFile.close()


def addIcon(pngName, pngFilename, iconPyFile, first):
    options = [
        "-F",
        "-i",
        "-c",
        "-a",
        "-n%s" % pngName,
        pngFilename,
        iconPyFile,
    ]
    if first:
        options.remove("-a")
    img2py.main(options)


def extractAndAddIcon(iconZipFile, iconPyFile, pngName, pngZipped, first):
    pngFilename = "%s.png" % pngName
    extractIcon(iconZipFile, pngFilename, pngZipped)
    addIcon(pngName, pngFilename, iconPyFile, first)
    os.remove(pngFilename)


def extractAndAddIcons(iconZipFile, iconPyFile):
    import iconmap

    first = True
    for pngName, pngZipped in list(iconmap.icons.items()):
        extractAndAddIcon(iconZipFile, iconPyFile, pngName, pngZipped, first)
        first = False


def makeIconPyFile(iconPyFile):
    if os.path.isfile(iconPyFile):
        os.remove(iconPyFile)

    import zipfile

    iconZipFile = zipfile.ZipFile("nuvola.zip", "r")
    extractAndAddIcons(iconZipFile, iconPyFile)
    iconZipFile.close()


def makeSplashScreen(iconPyFile):
    options = ["-F", "-c", "-a", "-nsplash", "splash.png", iconPyFile]
    img2py.main(options)


if __name__ == "__main__":
    iconFileName = "../taskcoachlib/gui/icons.py"
    makeIconPyFile(iconFileName)
    makeSplashScreen(iconFileName)
