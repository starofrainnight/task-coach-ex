'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2013 Task Coach developers <developers@taskcoach.org>

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
'''

from taskcoachlib import patterns
import weakref


class Attribute(object):
    __slots__ = ('__value', '__owner', '__setEvent')
    
    def __init__(self, value, owner, setEvent):
        super(Attribute, self).__init__()
        self.__value = value
        self.__owner = weakref.ref(owner)
        self.__setEvent = setEvent.im_func
        
    def get(self):
        return self.__value
    
    @patterns.eventSource
    def set(self, value, event=None):
        owner = self.__owner()
        if owner is not None:
            if value == self.__value:
                return False
            self.__value = value
            self.__setEvent(owner, event)
            return True
    

class SetAttribute(object):
    __slots__ = ('__set', '__owner', '__addEvent', '__removeEvent', 
                 '__changeEvent')
    
    def __init__(self, values, owner, addEvent=None, removeEvent=None, changeEvent=None):
        self.__set = set(values) if values else set()
        self.__owner = weakref.ref(owner)
        self.__addEvent = (addEvent or self.__nullEvent).im_func
        self.__removeEvent = (removeEvent or self.__nullEvent).im_func
        self.__changeEvent = (changeEvent or self.__nullEvent).im_func
        
    def get(self):
        return self.__set.copy()
    
    @patterns.eventSource
    def set(self, values, event=None):
        owner = self.__owner()
        if owner is not None:
            if values == self.__set:
                return False
            added = values - self.__set
            removed = self.__set - values
            self.__set = values
            if added:
                self.__addEvent(owner, event, *added) # pylint: disable=W0142
            if removed:
                self.__removeEvent(owner, event, *removed) # pylint: disable=W0142
            if added or removed:
                self.__changeEvent(owner, event, *self.__set)
            return True
    
    @patterns.eventSource            
    def add(self, values, event=None):
        owner = self.__owner()
        if owner is not None:
            if values <= self.__set:
                return False
            self.__set |= values
            self.__addEvent(owner, event, *values) # pylint: disable=W0142
            self.__changeEvent(owner, event, *self.__set)
            return True
    
    @patterns.eventSource                    
    def remove(self, values, event=None):
        owner = self.__owner()
        if owner is not None:
            if values & self.__set == set():
                return False
            self.__set -= values
            self.__removeEvent(owner, event, *values) # pylint: disable=W0142
            self.__changeEvent(owner, event, *self.__set)
            return True

    def __nullEvent(self, *args, **kwargs):
        pass
