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

from taskcoachlib.domain import base
from taskcoachlib import patterns


class CategorizableContainer(base.Collection):
    @patterns.eventSource
    def extend(self, items, event=None):
        super().extend(items, event=event)
        for item in self._compositesAndAllChildren(items):
            for category in item.categories():
                category.addCategorizable(item, event=event)

    @patterns.eventSource
    def removeItems(self, items, event=None):
        super().removeItems(items, event=event)
        for item in self._compositesAndAllChildren(items):
            for category in item.categories():
                category.removeCategorizable(item, event=event)
