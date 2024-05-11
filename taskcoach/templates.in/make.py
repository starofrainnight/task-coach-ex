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

import os
import xml.etree.ElementTree as ET


def dumpTemplate(filename, fd):
    path, name = os.path.split(filename)
    name, ext = os.path.splitext(name)

    if ext == ".tsktmpl":
        fd.write(
            "    templates.append((%s, %s))\n"
            % (repr(name), repr(open(filename, "rb").read()))
        )
        tree = ET.parse(open(filename, "rb"))
        root = tree.getroot()
        subject = root.find("task").attrib["subject"]
        fd.write("    _(%s)\n" % repr(subject.encode("UTF-8")))


def dumpDirectory(path):
    fd = open(
        os.path.join(
            "..", "taskcoachlib", "persistence", "xml", "templates.py"
        ),
        "w",
        encoding="utf-8",
    )
    fd.write("# -*- coding: UTF-8 -*-\n\n")
    fd.write("from taskcoachlib.i18n import _\n\n")
    fd.write("def getDefaultTemplates():\n")
    fd.write("    templates = []\n")

    for name in os.listdir(path):
        dumpTemplate(os.path.join(path, name), fd)

    fd.write("\n    return templates\n")


if __name__ == "__main__":
    dumpDirectory(".")
