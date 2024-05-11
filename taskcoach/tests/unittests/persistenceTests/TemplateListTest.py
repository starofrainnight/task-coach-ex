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

import test, xml
from taskcoachlib import persistence


class Fake(object):
    def __init__(self, *args, **kwargs):
        pass


class TemplateReaderThatThrowsTooNewException(Fake):
    def read(self, *args, **kwargs):  # pylint: disable=W0613
        raise persistence.xml.reader.XMLReaderTooNewException


class TemplateReaderThatThrowsIOError(Fake):
    def read(self, *args, **kwargs):  # pylint: disable=W0613
        raise IOError


class TemplateReaderThatThrowsParseError(Fake):
    def read(self, *args, **kwargs):  # pylint: disable=W0613
        raise xml.etree.ElementTree.ParseError


class FakeFileClass(Fake):
    def close(self):
        pass


class FileClassThatRaisesIOError(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=W0613
        raise IOError


class TemplateListUnderTest(persistence.TemplateList):
    def _templateFilenames(self):
        return ["dummy.tsktmpl"]


class TemplateListTestCase(test.TestCase):
    def testPathWithoutTemplates(self):
        templateList = persistence.TemplateList(".")
        self.assertEqual([], templateList.tasks())

    def testHandleTooNewException(self):
        templateList = TemplateListUnderTest(
            ".", TemplateReaderThatThrowsTooNewException, FakeFileClass
        )
        self.assertEqual([], templateList.tasks())

    def testHandleIOErrorWhileOpeningFile(self):
        templateList = TemplateListUnderTest(
            ".", openFile=FileClassThatRaisesIOError
        )
        self.assertEqual([], templateList.tasks())

    def testHandleIOErrorWhileReadingTemplate(self):
        templateList = TemplateListUnderTest(
            ".", TemplateReaderThatThrowsIOError, FakeFileClass
        )
        self.assertEqual([], templateList.tasks())

    def testHandleParseErrorWhileReadingTemplate(self):
        templateList = TemplateListUnderTest(
            ".", TemplateReaderThatThrowsParseError, FakeFileClass
        )
        self.assertEqual([], templateList.tasks())
