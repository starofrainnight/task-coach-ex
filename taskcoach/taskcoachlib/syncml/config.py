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

"""

Classes for storing Funambol client configuration

"""


class SyncMLConfigNode(object):
    def __init__(self, name):
        super(SyncMLConfigNode, self).__init__()

        self.name = name

        self.__children = []
        self.__properties = {}

    def children(self):
        return self.__children

    def properties(self):
        return list(self.__properties.items())

    def addChild(self, child):
        self.__children.append(child)

    def get(self, name):
        return self.__properties.get(name, "")

    def set(self, name, value):
        self.__properties[name] = value

    def __getitem__(self, name):
        for child in self.__children:
            if child.name == name:
                return child
        raise KeyError(name)


def createDefaultSyncConfig(uid):
    cfg = SyncMLConfigNode("root")
    root = SyncMLConfigNode("TaskCoach-%s" % uid)
    cfg.addChild(root)
    spds = SyncMLConfigNode("spds")
    root.addChild(spds)
    sources = SyncMLConfigNode("sources")
    spds.addChild(sources)
    syncml = SyncMLConfigNode("syncml")
    spds.addChild(syncml)
    tasks = SyncMLConfigNode("TaskCoach-%s.Tasks" % uid)
    sources.addChild(tasks)
    notes = SyncMLConfigNode("TaskCoach-%s.Notes" % uid)
    sources.addChild(notes)
    auth = SyncMLConfigNode("Auth")
    syncml.addChild(auth)
    conn = SyncMLConfigNode("Conn")
    syncml.addChild(conn)

    return cfg
