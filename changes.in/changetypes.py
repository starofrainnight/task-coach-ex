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

import textwrap


class Release:
    def __init__(
        self,
        number,
        date,
        bugsFixed=None,
        featuresAdded=None,
        featuresRemoved=None,
        featuresChanged=None,
        dependenciesChanged=None,
        implementationChanged=None,
        websiteChanges=None,
        distributionsChanged=None,
        teamChanges=None,
        summary="",
    ):
        self.number = number
        self.date = date
        self.summary = summary
        self.bugsFixed = bugsFixed or []
        self.featuresAdded = featuresAdded or []
        self.featuresRemoved = featuresRemoved or []
        self.featuresChanged = featuresChanged or []
        self.dependenciesChanged = dependenciesChanged or []
        self.implementationChanged = implementationChanged or []
        self.websiteChanges = websiteChanges or []
        self.distributionsChanged = distributionsChanged or []
        self.teamChanges = teamChanges or []


class Change(object):
    def __init__(self, description, *changeIds):
        self.description = description
        self.changeIds = changeIds


class Bug(Change):
    pass


class Bugv2(Bug):
    pass


class Feature(Change):
    pass


class Dependency(Change):
    pass


class Implementation(Change):
    pass


class Distribution(Change):
    pass


class Website(Change):
    def __init__(self, description, url, *changeIds):
        super(Website, self).__init__(description, *changeIds)
        self.url = url


class Team(Change):
    pass
