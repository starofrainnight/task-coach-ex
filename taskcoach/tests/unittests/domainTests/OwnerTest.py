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
from taskcoachlib.domain import base
from taskcoachlib import patterns


class OwnerUnderTest(base.Object, metaclass=base.DomainObjectOwnerMetaclass):
    __ownedType__ = "Foo"


class Foo(object):
    pass


class OwnerTest(test.TestCase):
    def setUp(self):
        self.owner = OwnerUnderTest()
        self.events = []

    def onEvent(self, event):
        self.events.append(event)

    # pylint: disable=E1101

    def testSetObjects_NoNotificationWhenUnchanged(self):
        patterns.Publisher().registerObserver(
            self.onEvent, self.owner.foosChangedEventType()
        )
        self.owner.setFoos([])
        self.assertFalse(self.events)

    def testSetObjects_NotificationWhenCanged(self):
        patterns.Publisher().registerObserver(
            self.onEvent, self.owner.foosChangedEventType()
        )
        self.owner.setFoos([Foo()])
        self.assertEqual(1, len(self.events))

    def testRemoveNoObjects(self):
        self.owner.removeFoos()
        self.assertFalse(self.owner.foos())
