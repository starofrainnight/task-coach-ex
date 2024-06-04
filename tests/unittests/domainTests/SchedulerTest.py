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

import test, time
from taskcoachlib.domain import date


class SchedulerTest(test.TestCase):
    def setUp(self):
        super(SchedulerTest, self).setUp()
        self.scheduler = date.Scheduler()
        self.callCount = 0

    def callback(self):
        self.callCount += 1

    @test.skipOnTwistedVersions("12.")
    def testScheduleAtDateTime(self):
        futureDate = date.Now() + date.TimeDelta(seconds=1)
        self.scheduler.schedule(self.callback, futureDate)
        self.assertTrue(self.scheduler.is_scheduled(self.callback))
        t0 = time.time()
        from twisted.internet import reactor

        while time.time() - t0 < 2.1:
            reactor.iterate()
        self.assertFalse(self.scheduler.is_scheduled(self.callback))
        self.assertEqual(self.callCount, 1)

    @test.skipOnTwistedVersions("12.")
    def testUnschedule(self):
        futureDate = date.Now() + date.TimeDelta(seconds=1)
        self.scheduler.schedule(self.callback, futureDate)
        self.scheduler.unschedule(self.callback)
        self.assertFalse(self.scheduler.is_scheduled(self.callback))
        t0 = time.time()
        from twisted.internet import reactor

        while time.time() - t0 < 1.2:
            reactor.iterate()
        self.assertEqual(self.callCount, 0)

    @test.skipOnTwistedVersions("12.")
    def testScheduleAtPastDateTime(self):
        pastDate = date.Now() - date.TimeDelta(seconds=1)
        self.scheduler.schedule(self.callback, pastDate)
        self.assertFalse(self.scheduler.is_scheduled(self.callback))
        from twisted.internet import reactor

        reactor.iterate()
        self.assertFalse(self.scheduler.is_scheduled(self.callback))
        self.assertEqual(self.callCount, 1)

    @test.skipOnTwistedVersions("12.")
    def testScheduleInterval(self):
        self.scheduler.schedule_interval(self.callback, seconds=1)
        try:
            t0 = time.time()
            from twisted.internet import reactor

            while time.time() - t0 < 2.1:
                reactor.iterate()
            self.assertEqual(self.callCount, 2)
        finally:
            self.scheduler.unschedule(self.callback)
