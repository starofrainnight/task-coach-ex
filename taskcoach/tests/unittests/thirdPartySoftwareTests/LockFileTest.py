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

import test, tempfile
from taskcoachlib.thirdparty import lockfile


class LockFileTest(test.TestCase):
    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile()
        self.lock = lockfile.FileLock(self.tmpfile.name)

    def tearDown(self):
        super(LockFileTest, self).tearDown()
        self.tmpfile.close()  # Temp files are deleted when closed

    def testFileIsNotLockedInitially(self):
        self.assertFalse(self.lock.is_locked())

    def testFileIsLockedAfterLocking(self):
        self.lock.acquire()
        self.assertTrue(self.lock.is_locked())

    def testLockingWithContextManager(self):
        with self.lock:
            self.assertTrue(self.lock.is_locked())
        self.assertFalse(self.lock.is_locked())

    def testLockingTwoFiles(self):
        self.lock.acquire()
        tmpfile2 = tempfile.NamedTemporaryFile()
        lock2 = lockfile.FileLock(tmpfile2.name)
        lock2.acquire()
        self.assertTrue(self.lock.is_locked())
        self.assertTrue(lock2.is_locked())
