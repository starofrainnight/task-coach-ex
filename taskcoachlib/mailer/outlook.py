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

import os, stat, codecs
from taskcoachlib import persistence


if os.name == "nt":
    from win32com.client import GetActiveObject  # pylint: disable=F0401

    def getCurrentSelection():
        selection = (
            GetActiveObject("Outlook.Application").ActiveExplorer().Selection
        )
        filenames = []
        for n in range(1, selection.Count + 1):
            filename = persistence.get_temp_file(suffix=".eml")
            saveItem(selection.Item(n), filename)
            filenames.append(filename)
        return filenames

    def saveItem(item, filename):
        body = item.Body
        encoding = "iso-8859-1"
        try:
            codecs.encode(body, encoding)
        except UnicodeEncodeError:
            encoding = "utf-8"
        mailFile = codecs.open(filename, "wb", encoding)
        try:
            mailFile.write(emailHeaders(item, encoding) + body)
        finally:
            mailFile.close()
            os.chmod(filename, stat.S_IREAD)

    def emailHeaders(item, encoding, lineSep="\r\n"):
        headers = []
        headers.append("subject: %s" % item.Subject)
        headers.append("X-Outlook-ID: %s" % item.EntryID)
        headers.append("Content-Transfer-Encoding: %s" % encoding)
        headers.append(lineSep)
        return lineSep.join(headers)
