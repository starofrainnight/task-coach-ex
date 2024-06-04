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

import re
import sre_constants
from taskcoachlib import patterns
from taskcoachlib.domain.base import object as domainobject


class Filter(patterns.SetDecorator):
    def __init__(self, *args, **kwargs):
        self.__treeMode = kwargs.pop("treeMode", False)
        super(Filter, self).__init__(*args, **kwargs)
        self.reset()

    def thaw(self):
        super(Filter, self).thaw()
        if not self.isFrozen():
            self.reset()

    def setTreeMode(self, treeMode):
        self.__treeMode = treeMode
        try:
            self.observable().setTreeMode(treeMode)
        except AttributeError:
            pass
        self.reset()

    def treeMode(self):
        return self.__treeMode

    @patterns.eventSource
    def reset(self, event=None):
        if self.isFrozen():
            return

        filteredItems = set(self.filterItems(self.observable()))
        if self.treeMode():
            for item in filteredItems.copy():
                filteredItems.update(set(item.ancestors()))
        self.removeItemsFromSelf(
            [item for item in self if item not in filteredItems], event=event
        )
        self.extendSelf(
            [item for item in filteredItems if item not in self], event=event
        )

    def filterItems(self, items):
        """filter returns the items that pass the filter."""
        raise NotImplementedError  # pragma: no cover

    def rootItems(self):
        return [item for item in self if item.parent() is None]

    def onAddItem(self, event):
        self.reset()

    def onRemoveItem(self, event):
        self.reset()


class SelectedItemsFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__selectedItems = set(kwargs.pop("selectedItems", []))
        self.__includeSubItems = kwargs.pop("includeSubItems", True)
        super(SelectedItemsFilter, self).__init__(*args, **kwargs)

    @patterns.eventSource
    def removeItemsFromSelf(self, items, event=None):
        super(SelectedItemsFilter, self).removeItemsFromSelf(items, event)
        self.__selectedItems.difference_update(set(items))
        if not self.__selectedItems:
            self.extendSelf(self.observable(), event)

    def filterItems(self, items):
        if self.__selectedItems:
            result = [
                item
                for item in items
                if self.itemOrAncestorInSelectedItems(item)
            ]
            if self.__includeSubItems:
                for item in result[:]:
                    result.extend(item.children(recursive=True))
            return result
        else:
            return [item for item in items if item not in self]

    def itemOrAncestorInSelectedItems(self, item):
        if item in self.__selectedItems:
            return True
        elif item.parent():
            return self.itemOrAncestorInSelectedItems(item.parent())
        else:
            return False


class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        searchString = kwargs.pop("searchString", "")
        matchCase = kwargs.pop("matchCase", False)
        includeSubItems = kwargs.pop("includeSubItems", False)
        searchDescription = kwargs.pop("searchDescription", False)
        regularExpression = kwargs.pop("regularExpression", False)

        self.setSearchFilter(
            searchString,
            matchCase=matchCase,
            includeSubItems=includeSubItems,
            searchDescription=searchDescription,
            regularExpression=regularExpression,
            doReset=False,
        )

        super(SearchFilter, self).__init__(*args, **kwargs)

    def setSearchFilter(
        self,
        searchString,
        matchCase=False,
        includeSubItems=False,
        searchDescription=False,
        regularExpression=False,
        doReset=True,
    ):
        # pylint: disable=W0201
        self.__includeSubItems = includeSubItems
        self.__searchDescription = searchDescription
        self.__regularExpression = regularExpression
        self.__searchPredicate = self.__compileSearchPredicate(
            searchString, matchCase, regularExpression
        )
        if doReset:
            self.reset()

    @staticmethod
    def __compileSearchPredicate(searchString, matchCase, regularExpression):
        if not searchString:
            return ""
        flag = 0 if matchCase else re.IGNORECASE | re.UNICODE
        if regularExpression:
            try:
                rx = re.compile(searchString, flag)
            except sre_constants.error:
                if matchCase:
                    return lambda x: x.find(searchString) != -1
                else:
                    return lambda x: x.lower().find(searchString.lower()) != -1
            else:
                return rx.search
        elif matchCase:
            return lambda x: x.find(searchString) != -1
        else:
            return lambda x: x.lower().find(searchString.lower()) != -1

    def filterItems(self, items):
        return (
            [
                item
                for item in items
                if self.__searchPredicate(self.__itemText(item))
            ]
            if self.__searchPredicate
            else items
        )

    def __itemText(self, item):
        text = self.__itemOwnText(item)
        if self.__includeSubItems:
            parent = item.parent()
            while parent:
                text += self.__itemOwnText(parent)
                parent = parent.parent()
        if self.treeMode():
            text += " ".join(
                [
                    self.__itemOwnText(child)
                    for child in item.children(recursive=True)
                    if child in self.observable()
                ]
            )
        return text

    def __itemOwnText(self, item):
        text = item.subject()
        if self.__searchDescription:
            text += item.description()
        return text


class DeletedFilter(Filter):
    def __init__(self, *args, **kwargs):
        super(DeletedFilter, self).__init__(*args, **kwargs)

        for eventType in [
            domainobject.Object.markDeletedEventType(),
            domainobject.Object.markNotDeletedEventType(),
        ]:
            patterns.Publisher().registerObserver(
                self.onObjectMarkedDeletedOrNot, eventType=eventType
            )

    def detach(self):
        patterns.Publisher().removeObserver(self.onObjectMarkedDeletedOrNot)
        super(DeletedFilter, self).detach()

    def onObjectMarkedDeletedOrNot(self, event):  # pylint: disable=W0613
        self.reset()

    def filterItems(self, items):
        return [item for item in items if not item.isDeleted()]
