"""
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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

# inotify wrapper from this recipe: http://code.activestate.com/recipes/576375-low-level-inotify-wrapper/
# Slightly modified to handle timeout and use select(); cleanup error handling

from twisted.internet.inotify import INotify
from twisted.python.filepath import FilePath

from taskcoachlib.filesystem import base
import os


class FilesystemNotifier(base.NotifierBase):
    def __init__(self):
        super(FilesystemNotifier, self).__init__()

        self.notifier = INotify()
        self.notifier.startReading()

    def setFilename(self, filename):
        if self._path is not None:
            self.notifier.ignore(FilePath(self._path))
        super(FilesystemNotifier, self).setFilename(filename)
        if self._path is not None:
            self.notifier.watch(
                FilePath(self._path), callbacks=[self.__notify]
            )

    def stop(self):
        if self.notifier is not None:
            self.notifier.stopReading()
            self.notifier = None

    def __notify(self, handle, filepath, mask):
        myName = self._filename
        if myName is not None:
            if filepath.basename() == os.path.split(myName)[-1]:
                if self._check(myName) and myName:
                    self.stamp = os.stat(myName).st_mtime
                    self.onFileChanged()

    def onFileChanged(self):
        raise NotImplementedError
