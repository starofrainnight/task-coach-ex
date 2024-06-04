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

import test, io
from taskcoachlib import persistence, config
from taskcoachlib.domain import task, date


class TemplateXMLWriterTestCase(test.TestCase):
    def setUp(self):
        task.Task.settings = config.Settings(load=False)
        self.fd = io.StringIO()
        self.fd.name = "testfile.tsk"
        self.fd.encoding = "utf-8"
        self.writer = persistence.TemplateXMLWriter(self.fd)
        self.task = task.Task()

    def __writeAndRead(self):
        self.writer.write(self.task)
        return self.fd.getvalue()

    def expectInXML(self, xmlFragment):
        xml = self.__writeAndRead()
        self.assertTrue(
            xmlFragment in xml, "%s not in %s" % (xmlFragment, xml)
        )

    # tests

    def testDefaultTask(self):
        self.expectInXML(
            '<tasks>\n<task creationDateTime="%s" id="%s" '
            'status="1" />\n</tasks>'
            % (self.task.creationDateTime(), self.task.id())
        )

    def testTaskWithPlannedStartDateTime(self):
        self.task.setPlannedStartDateTime(
            date.Now() + date.TimeDelta(minutes=31)
        )
        self.expectInXML('plannedstartdatetmpl="31 minutes from now')

    def testTaskWithDueDateTime(self):
        self.task.setDueDateTime(date.Now() + date.TimeDelta(minutes=13))
        self.expectInXML('duedatetmpl="13 minutes from now')

    def testTaskWithCompletionDateTime(self):
        self.task.setCompletionDateTime(date.Now() + date.TimeDelta(minutes=4))
        self.expectInXML('completiondatetmpl="4 minutes from now')

    def testTaskWithReminder(self):
        self.task.setReminder(date.Now() + date.TimeDelta(seconds=10))
        self.expectInXML('remindertmpl="0 minutes from now')
