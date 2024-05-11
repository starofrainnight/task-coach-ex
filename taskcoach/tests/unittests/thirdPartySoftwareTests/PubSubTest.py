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

from taskcoachlib.thirdparty.pubsub import pub
import test


class PubSubTest(test.TestCase):
    def setUp(self):
        self.calledTestTopic = False

    def onTestTopic(self):
        self.calledTestTopic = True

    def testSubscribe(self):
        pub.subscribe(self.onTestTopic, "TestTopic")
        pub.sendMessage("TestTopic")
        self.assertTrue(self.calledTestTopic)
