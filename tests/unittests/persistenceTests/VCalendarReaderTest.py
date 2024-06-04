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
from taskcoachlib import persistence
from taskcoachlib.domain import date


class VCalendarParserTest(test.TestCase):
    # pylint: disable=W0511

    def setUp(self):
        self.parser = persistence.icalendar.ical.VCalendarParser()

    def testEmptyVCalender(self):
        self.parser.parse(["BEGIN:VCALENDAR", "END:VCALENDAR"])
        self.assertFalse(self.parser.tasks)

    def testEmptyVTodo(self):
        self.parser.parse(["BEGIN:VTODO", "END:VTODO"])
        self.assertEqual(
            dict(status=0, plannedStartDateTime=date.DateTime()),
            self.parser.tasks[0],
        )

    def testSubject(self):
        self.parser.parse(["BEGIN:VTODO", "SUBJECT:Test", "END:VTODO"])
        self.assertEqual(
            dict(
                status=0, subject="Test", plannedStartDateTime=date.DateTime()
            ),
            self.parser.tasks[0],
        )

    def testDueDate(self):
        self.parser.parse(["BEGIN:VTODO", "DUE:20100101T120000", "END:VTODO"])
        self.assertEqual(
            dict(
                status=0,
                dueDateTime=date.DateTime(2010, 1, 1, 12, 0, 0),
                plannedStartDateTime=date.DateTime(),
            ),
            self.parser.tasks[0],
        )

    def testPercentageComplete(self):
        self.parser.parse(["BEGIN:VTODO", "PERCENT-COMPLETE:56", "END:VTODO"])
        self.assertEqual(
            dict(
                status=0,
                percentageComplete=56,
                plannedStartDateTime=date.DateTime(),
            ),
            self.parser.tasks[0],
        )

    def testCreationDateTime(self):
        self.parser.parse(
            ["BEGIN:VTODO", "CREATED:20100101T120000", "END:VTODO"]
        )
        self.assertEqual(
            dict(
                status=0,
                creationDateTime=date.DateTime(2010, 1, 1, 12, 0, 0),
                plannedStartDateTime=date.DateTime(),
            ),
            self.parser.tasks[0],
        )

    def testModificationDateTime(self):
        self.parser.parse(
            ["BEGIN:VTODO", "LAST-MODIFIED:20100101T120000", "END:VTODO"]
        )
        self.assertEqual(
            dict(
                status=0,
                modificationDateTime=date.DateTime(2010, 1, 1, 12, 0, 0),
                plannedStartDateTime=date.DateTime(),
            ),
            self.parser.tasks[0],
        )


class VNoteParserTest(test.TestCase):
    def setUp(self):
        self.parser = persistence.icalendar.ical.VNoteParser()

    def testEmptyVCalendar(self):
        self.parser.parse(["BEGIN:VCALENDAR", "END:VCALENDAR"])
        self.assertFalse(self.parser.notes)

    def testEmptyVNote(self):
        self.parser.parse(["BEGIN:VNOTE", "END:VNOTE"])
        self.assertEqual(dict(status=0, subject=""), self.parser.notes[0])

    def testSubject(self):
        self.parser.parse(["BEGIN:VNOTE", "SUMMARY:Subject", "END:VNOTE"])
        self.assertEqual(
            dict(status=0, subject="Subject"), self.parser.notes[0]
        )

    def testCreationDateTime(self):
        self.parser.parse(
            ["BEGIN:VNOTE", "CREATED:20100101T120000", "END:VNOTE"]
        )
        self.assertEqual(
            dict(
                status=0,
                subject="",
                creationDateTime=date.DateTime(2010, 1, 1, 12, 0, 0),
            ),
            self.parser.notes[0],
        )

    def testModificationDateTime(self):
        self.parser.parse(
            ["BEGIN:VNOTE", "LAST-MODIFIED:20100101T120000", "END:VNOTE"]
        )
        self.assertEqual(
            dict(
                status=0,
                subject="",
                modificationDateTime=date.DateTime(2010, 1, 1, 12, 0, 0),
            ),
            self.parser.notes[0],
        )
