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

from taskcoachlib.persistence.icalendar import ical
from taskcoachlib.domain import task
from taskcoachlib import meta


def extendedWithAncestors(selection):
    extendedSelection = selection[:]
    for item in selection:
        for ancestor in item.ancestors():
            if ancestor not in extendedSelection:
                extendedSelection.append(ancestor)
    return extendedSelection


class iCalendarWriter(object):
    def __init__(self, fd, filename=None):
        self.__fd = fd

    def write(
        self, viewer, settings, selectionOnly=False
    ):  # pylint: disable=W0613
        items = viewer.visibleItems()
        if selectionOnly:
            selection = viewer.curselection()
            if viewer.isTreeViewer():
                selection = extendedWithAncestors(selection)
            items = [item for item in items if item in selection]
        return self.writeItems(items)

    def writeItems(self, items):
        self.__fd.write("BEGIN:VCALENDAR\r\n")
        self._writeMetaData()
        count = 0
        for item in items:
            transform = (
                ical.VCalFromTask
                if isinstance(item, task.Task)
                else ical.VCalFromEffort
            )
            self.__fd.write(transform(item, encoding=False))
            count += 1
        self.__fd.write("END:VCALENDAR\r\n")
        return count

    def _writeMetaData(self):
        self.__fd.write("VERSION:2.0\r\n")
        domain = meta.url[len("http://") :].strip("/")
        self.__fd.write(
            "PRODID:-//%s//NONSGML %s V%s//EN\r\n"
            % (domain, meta.name, meta.version)
        )
