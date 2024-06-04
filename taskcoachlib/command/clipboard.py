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

from taskcoachlib import patterns


class Clipboard(metaclass=patterns.Singleton):
    def __init__(self):
        self.clear()

    def put(self, items, source):
        # pylint: disable=W0201
        self._contents = items
        self._source = source

    def get(self):
        currentContents = self._contents
        currentSource = self._source
        return currentContents, currentSource

    def peek(self):
        return self._contents

    def clear(self):
        self._contents = []
        self._source = None

    def __bool__(self):
        return len(self._contents) > 0
