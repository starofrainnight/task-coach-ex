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

# Script to update copyright notices.

import os, datetime

copyright_notice = (
    "Copyright (C) 2004-%s Task Coach developers <developers@taskcoach.org>"
)
year = datetime.date.today().year
copyright_notice_last_year = copyright_notice % (year - 1)
copyright_notice_this_year = copyright_notice % (year)


def change_copyright_notice(filepath):
    with open(filepath, "r") as fp:
        contents = fp.read()
    if copyright_notice_last_year in contents:
        print("updating", filepath)
        contents = contents.replace(
            copyright_notice_last_year, copyright_notice_this_year, 1
        )
        with open(filepath, "w") as fp:
            fp.write(contents)
    else:
        print("skipping", filepath)


for dirpath, dirnames, filenames in os.walk(".."):
    for dirname in dirnames[:]:
        if dirname.startswith(".") and not dirname.startswith(".."):
            dirnames.remove(dirname)
    for filename in filenames:
        change_copyright_notice(os.path.join(dirpath, filename))
