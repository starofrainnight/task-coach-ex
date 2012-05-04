'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>
Copyright (C) 2008 Thomas Sonne Olesen <tpo@sonnet.dk>

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

''' This module provides classes that implement refreshing strategies for
    viewers. '''  # pylint: disable-msg=W0105


from taskcoachlib import patterns
from taskcoachlib.domain import date
from taskcoachlib.thirdparty.pubsub import pub


class MinuteRefresher(object):
    ''' This class can be used by viewers to refresh themselves every minute
        to refresh attributes like time left. The user of this class is
        responsible for calling refresher.startClock() and stopClock(). '''

    def __init__(self, viewer):
        self.__viewer = viewer        
        
    def startClock(self):
        date.Scheduler().schedule_interval(self.onEveryMinute, minutes=1)
        
    def stopClock(self):
        date.Scheduler().unschedule(self.onEveryMinute)
        
    def onEveryMinute(self):
        if self.__viewer:
            self.__viewer.refresh()
        else:
            self.stopClock()


class SecondRefresher(patterns.Observer):
    ''' This class can be used by viewers to refresh themselves every second
        whenever items (tasks, efforts) are being tracked. '''
        
    def __init__(self, viewer, trackingChangedEventType):
        super(SecondRefresher, self).__init__()
        self.__viewer = viewer
        self.__presentation = viewer.presentation()
        self.__trackedItems = set()
        pub.subscribe(self.onTrackingChanged, trackingChangedEventType)
        self.registerObserver(self.onItemAdded, 
                              eventType=self.__presentation.addItemEventType(),
                              eventSource=self.__presentation)
        self.registerObserver(self.onItemRemoved, 
                              eventType=self.__presentation.removeItemEventType(),
                              eventSource=self.__presentation)
        self.setTrackedItems(self.trackedItems(self.__presentation))

    def onItemAdded(self, event):
        self.addTrackedItems(self.trackedItems(event.values()))
        
    def onItemRemoved(self, event): 
        self.removeTrackedItems(self.trackedItems(event.values()))

    def onTrackingChanged(self, newValue, sender):
        if sender not in self.__presentation:
            return
        if newValue:
            self.addTrackedItems([sender])
        else:
            self.removeTrackedItems([sender])
        self.refreshItems([sender])

    def onEverySecond(self):
        self.refreshItems(self.__trackedItems)
        
    def refreshItems(self, items):
        if self.__viewer:
            self.__viewer.refreshItems(*items)  # pylint: disable-msg=W0142
        else:
            self.stopClock()

    def setTrackedItems(self, items):
        self.__trackedItems = set(items)
        self.startOrStopClock()
        
    def updatePresentation(self):
        self.__presentation = self.__viewer.presentation()
        self.setTrackedItems(self.trackedItems(self.__presentation))
        
    def addTrackedItems(self, items):
        if items:
            self.__trackedItems.update(items)
            self.startOrStopClock()

    def removeTrackedItems(self, items):
        if items:
            self.__trackedItems.difference_update(items)
            self.startOrStopClock()

    def startOrStopClock(self):
        if self.__trackedItems:
            self.startClock()
        else:
            self.stopClock()
            
    def startClock(self):
        date.Scheduler().schedule_interval(self.onEverySecond, seconds=1)
            
    def stopClock(self):
        date.Scheduler().unschedule(self.onEverySecond)
    
    def currentlyTrackedItems(self):
        return list(self.__trackedItems)

    @staticmethod
    def trackedItems(items):
        return [item for item in items if item.isBeingTracked(recursive=True)]
