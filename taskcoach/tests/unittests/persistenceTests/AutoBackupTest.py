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

import test, os, shutil, bz2
from taskcoachlib import persistence, config
from taskcoachlib.domain import date, task


class DummyFile(object):
    encoding = "utf-8"
    name = "whatever.tsk"

    def close(self, *args, **kwargs):  # pylint: disable=W0613
        pass

    def write(self, *args, **kwargs):  # pylint: disable=W0613
        pass


class DummyTaskFile(persistence.TaskFile):
    def _openForRead(self, *args, **kwargs):  # pylint: disable=W0613
        return DummyFile()

    def _openForWrite(self, *args, **kwargs):  # pylint: disable=W0613
        return DummyFile()

    def _read(self, *args, **kwargs):  # pylint: disable=W0613
        return [task.Task()], [], [], None, dict(), None

    def exists(self):
        return True

    def filename(self):
        return super(DummyTaskFile, self).filename() or "whatever.tsk"


class LocalSettings(config.Settings):
    def __init__(self, *args, **kwargs):
        self.__path = os.path.join(os.getcwd(), "testdata")
        if os.path.exists(self.__path):
            shutil.rmtree(self.__path)
        os.mkdir(self.__path)
        super(LocalSettings, self).__init__(*args, **kwargs)

    def _pathToDataDir(self, *args, **kwargs):
        return self.__path, False


class AutoBackupTest(test.TestCase):
    # pylint: disable=E1101,E1002,W0232
    def setUp(self):
        super(AutoBackupTest, self).setUp()
        task.Task.settings = self.settings = LocalSettings(load=False)
        self.taskFile = DummyTaskFile()
        self.backup = persistence.AutoBackup(
            self.settings, copyfile=self.onCopyFile
        )
        self.copyCalled = False

    def tearDown(self):
        super(AutoBackupTest, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()
        if os.path.exists("test.tsk"):
            os.remove("test.tsk")

    def onCopyFile(self, *args):  # pylint: disable=W0613
        self.copyCalled = True

    def oneBackupFile(self):
        return [self.backup.backupFilename(self.taskFile)]

    def fourBackupFiles(self):
        files = [
            self.backup.backupFilename(self.taskFile),
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2001, 1, 1, 1, 1, 1)
            ),
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2002, 1, 1, 1, 1, 1)
            ),
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2000, 1, 1, 1, 1, 1)
            ),
        ]
        files.sort()
        return files

    def fiveBackupFiles(self):
        files = [
            self.backup.backupFilename(self.taskFile),
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2001, 1, 1, 1, 1, 1)
            ),
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2002, 1, 1, 1, 1, 1)
            ),
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2002, 1, 1, 1, 1, 2)
            ),
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2000, 1, 1, 1, 1, 1)
            ),
        ]
        files.sort()
        return files

    def globMany(self, pattern):  # pylint: disable=W0613
        return self.manyBackupFiles()

    def manyBackupFiles(self):
        files = [self.backup.backupFilename(self.taskFile)] * 100 + [
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2000, 1, 1, 1, 1, 1)
            )
        ]
        files.sort()
        return files

    def testBackupMigrationManifest(self):
        self.taskFile.setFilename("test.tsk")
        self.backup.onTaskFileRead(self.taskFile)
        with open(
            os.path.join(self.settings.pathToBackupsDir(), "backups.xml"), "rb"
        ) as fp:
            content = fp.read()
        self.assertEqual(
            content,
            '<backupfiles><file sha="13cf6835565aaf4ab1f78e922b9917f9a4c7a856">test.tsk</file></backupfiles>',
        )

    def testBackupMigration(self):
        self.taskFile.setFilename("test.tsk")
        with open("test.20140715-010203.tsk.bak", "wb") as fp:
            fp.write("Hello, world")
        self.backup.onTaskFileRead(self.taskFile)
        self.assertFalse(os.path.exists("test.20140715-010203.tsk.bak"))

        backupName = os.path.join(
            self.settings.pathToBackupsDir(),
            "13cf6835565aaf4ab1f78e922b9917f9a4c7a856",
            "20140715010203.bak",
        )
        self.assertTrue(os.path.exists(backupName))
        self.assertEqual(bz2.BZ2File(backupName).read(), "Hello, world")

    def testNoBackupFiles(self):
        self.assertEqual(
            [], self.backup.backupFiles(self.taskFile, glob=lambda pattern: [])
        )

    def testOneBackupFile(self):
        self.assertEqual(
            ["1"],
            self.backup.backupFiles(self.taskFile, glob=lambda pattern: ["1"]),
        )

    def testNotTooManyBackupFiles(self):
        self.assertEqual(
            0, self.backup.numberOfExtraneousBackupFiles(self.oneBackupFile())
        )

    def testTooManyBackupFiles_(self):
        self.assertEqual(
            85,
            self.backup.numberOfExtraneousBackupFiles(self.manyBackupFiles()),
        )

    def testRemoveExtraneousBackFiles(self):
        self.backup.maxNrOfBackupFilesToRemoveAtOnce = 100
        removedFiles = []

        def remove(filename):
            removedFiles.append(filename)

        self.backup.removeExtraneousBackupFiles(
            self.taskFile, remove=remove, glob=self.globMany
        )
        self.assertEqual(85, len(removedFiles))

    def testRemoveExtraneousBackFiles_OSError(self):
        def remove(filename):  # pylint: disable=W0613
            raise OSError

        self.backup.removeExtraneousBackupFiles(
            self.taskFile, remove=remove, glob=self.globMany
        )

    def testBackupFilename(self):
        now = date.DateTime(2004, 1, 1)
        self.assertEqual(
            os.path.join(
                self.settings.pathToBackupsDir(),
                "c81e25c3e04922232ab8eb87be8337c806a44209",
                "20040101000000.bak",
            ),
            self.backup.backupFilename(self.taskFile, lambda: now),
        )  # pylint: disable=W0212

    def testCreateBackupOnSave(self):
        self.taskFile.save()
        self.copyCalled = False
        self.taskFile.tasks().append(task.Task())
        self.taskFile.save()
        self.assertTrue(self.copyCalled)

    def testDontCreateBackupOnOpen(self):
        self.taskFile.load()
        self.assertFalse(self.copyCalled)

    def testDontCreateBackupWhenSettingFilename(self):
        self.taskFile.setFilename("newname.tsk")
        self.assertFalse(self.copyCalled)

    def testLeastUniqueBackupFile_FourBackupFiles(self):
        self.assertEqual(
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2001, 1, 1, 1, 1, 1)
            ),
            self.backup.leastUniqueBackupFile(self.fourBackupFiles()),
        )

    def testLeastUniqueBackupFile_FiveBackupFiles(self):
        self.assertEqual(
            self.backup.backupFilename(
                self.taskFile, now=lambda: date.DateTime(2002, 1, 1, 1, 1, 1)
            ),
            self.backup.leastUniqueBackupFile(self.fiveBackupFiles()),
        )
