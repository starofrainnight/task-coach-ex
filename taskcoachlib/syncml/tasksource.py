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

import inspect
from taskcoachlib.syncml import basesource
from taskcoachlib.domain.task import Task
from taskcoachlib.domain.category import Category
from taskcoachlib.persistence.icalendar import ical


class TaskSource(basesource.BaseSource):
    def __init__(self, callback, taskList, categoryList, *args, **kwargs):
        super().__init__(callback, taskList, *args, **kwargs)
        self.categoryList = categoryList

    def updateItemProperties(self, item, task):
        item.data = (
            "BEGIN:VCALENDAR\r\nVERSION: 1.0\r\n"
            + ical.VCalFromTask(task, doFold=False).encode("UTF-8")
            + "END:VCALENDAR"
        )
        item.dataType = "text/calendar"

    def _parseObject(self, item):
        parser = ical.VCalendarParser()
        parser.parse([x.rstrip("\r") for x in item.data.split("\n")])

        categories = parser.tasks[0].pop("categories", [])

        kwargs = dict(
            [
                (k, v)
                for k, v in list(parser.tasks[0].items())
                if k in inspect.getargspec(Task.__init__)[0]
            ]
        )
        task = Task(**kwargs)

        for category in categories:
            categoryObject = self.categoryList.findCategoryByName(category)
            if categoryObject is None:
                categoryObject = Category(category)
                self.categoryList.extend([categoryObject])
            task.addCategory(categoryObject)

        return task

    def doAddItem(self, task):
        for category in task.categories():
            category.addCategorizable(task)

        return 201

    def doUpdateItem(self, task, local):
        local.setPlannedStartDateTime(task.plannedStartDateTime())
        local.setDueDateTime(task.dueDateTime())
        local.setDescription(task.description())
        local.setSubject(task.subject())
        local.setPriority(task.priority())
        local.setCompletionDateTime(task.completionDateTime())

        for category in local.categories():
            category.removeCategorizable(local)

        local.setCategories(task.categories())

        for category in local.categories():
            category.addCategorizable(local)

        super().doUpdateItem(task, local)

        return 200  # FIXME
