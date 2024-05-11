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

from taskcoachlib import config, meta
from unittests import dummy
import io
import test


class DeveloperMessageCheckerUnderTest(meta.DeveloperMessageChecker):
    def __init__(self, *args, **kwargs):
        self.message_file_contents = "Message|http://a.b\n"
        kwargs["urlopen"] = self.urlopen
        kwargs["call_after"] = self.call_after
        super(DeveloperMessageCheckerUnderTest, self).__init__(*args, **kwargs)

    @staticmethod
    def call_after(function, *args, **kwargs):
        # Don't use wx.CallAfter in the tests
        return function(*args, **kwargs)

    def urlopen(self, url):  # pylint: disable=W0613
        return io.StringIO(self.message_file_contents)


class DeveloperMessageCheckerTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.checker = DeveloperMessageCheckerUnderTest(self.settings)

    def testDialogContainsMessage(self):
        dialog = self.checker.run(show=False)
        self.assertEqual("Message", dialog.current_message())

    def testDialogContainsURL(self):
        dialog = self.checker.run(show=False)
        self.assertEqual("http://a.b", dialog.current_url())

    def testNoMessage(self):
        self.checker.message_file_contents = ""
        self.assertEqual(None, self.checker.run(show=False))

    def testOnlyCommentInMessageFile(self):
        self.checker.message_file_contents = (
            "# This is a comment | even " "with a pipe symbol in it"
        )
        self.assertEqual(None, self.checker.run(show=False))

    def testCommentFollowedByEmptyLineInMessageFile(self):
        self.checker.message_file_contents = "# This is a comment\n\n"
        self.assertEqual(None, self.checker.run(show=False))

    def testCommentFollowedWithMessage(self):
        self.checker.message_file_contents = (
            "# This is a comment\n" "This is the message|url\n"
        )
        dialog = self.checker.run(show=False)
        self.assertEqual("This is the message", dialog.current_message())

    def testDontShowSameMessageTwice(self):
        dialog = self.checker.run(show=False)
        self.assertEqual("Message", dialog.current_message())
        dialog.on_close(dummy.Event())
        self.assertEqual(None, self.checker.run(show=False))
