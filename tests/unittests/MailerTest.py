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
import taskcoachlib.mailer


class TestMailer(test.TestCase):
    def testWriteMail(self):
        def openURL(mailtoString):
            self.mailtoString = mailtoString  # pylint: disable=W0201

        taskcoachlib.mailer.sendMail("to", "subject", "body", openURL=openURL)
        self.assertTrue(self.mailtoString.startswith("mailto:"))
