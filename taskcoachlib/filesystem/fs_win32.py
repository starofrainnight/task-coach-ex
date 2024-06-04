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

from win32file import *
from win32con import *
from win32event import *
import os, threading
from taskcoachlib.filesystem import base


class DirectoryWatcher(object):
    ADDED = 1
    REMOVED = 2
    MODIFIED = 3
    RENAMED_OLD = 4
    RENAMED_NEW = 5

    def __init__(self, path):
        super(DirectoryWatcher, self).__init__()

        self.dirHandle = CreateFile(
            path,
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_DELETE | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED,
            0,
        )
        self.buffer = AllocateReadBuffer(8192)
        self.overlapped = OVERLAPPED()
        self.overlapped.hEvent = CreateEvent(None, False, False, None)

    def wait(self, recurse=False, timeout=INFINITE):
        ReadDirectoryChangesW(
            self.dirHandle,
            self.buffer,
            recurse,
            FILE_NOTIFY_CHANGE_FILE_NAME
            | FILE_NOTIFY_CHANGE_DIR_NAME
            | FILE_NOTIFY_CHANGE_ATTRIBUTES
            | FILE_NOTIFY_CHANGE_SIZE
            | FILE_NOTIFY_CHANGE_LAST_WRITE,
            self.overlapped,
        )

        rc = WaitForSingleObject(self.overlapped.hEvent, timeout)
        if rc == WAIT_OBJECT_0:
            try:
                size = GetOverlappedResult(
                    self.dirHandle, self.overlapped, True
                )
            except Exception as e:
                if e.args[0] == 995:
                    return None
                raise
            if size == 0:
                return None
            else:
                return FILE_NOTIFY_INFORMATION(self.buffer, size)

    def stop(self):
        CloseHandle(self.dirHandle)


class FilesystemNotifier(base.NotifierBase):
    def __init__(self):
        super(FilesystemNotifier, self).__init__()

        self.watcher = None
        self.thread = None
        self.lock = threading.Lock()

    def setFilename(self, filename):
        self.lock.acquire()
        try:
            if self.watcher is not None:
                self.watcher.stop()
                self.thread.join()
                self.watcher = None
                self.thread = None
            super(FilesystemNotifier, self).setFilename(filename)
            if self._filename:
                self.watcher = DirectoryWatcher(self._path)
                self.thread = threading.Thread(target=self._run)
                self.thread.setDaemon(True)
                self.thread.start()
        finally:
            self.lock.release()

    def stop(self):
        self.lock.acquire()
        try:
            if self.watcher is not None:
                self.watcher.stop()
                self.thread.join()
                self.watcher = None
                self.thread = None
        finally:
            self.lock.release()

    def saved(self):
        with self.lock:
            super(FilesystemNotifier, self).saved()

    def onFileChanged(self):
        raise NotImplementedError

    def _run(self):
        while True:
            self.lock.acquire()
            try:
                watcher, myname = self.watcher, self._filename
            finally:
                self.lock.release()

            if watcher is not None:
                changes = watcher.wait()
                if changes is None:
                    return
                for change, name in changes:
                    if name == os.path.split(myname)[-1]:
                        if self._check(myname) and myname:
                            self.stamp = os.stat(myname).st_mtime
                            self.onFileChanged()
                            break
