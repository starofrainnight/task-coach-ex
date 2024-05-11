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

from taskcoachlib.syncml.tasksource import TaskSource
from taskcoachlib.syncml.notesource import NoteSource
from taskcoachlib.syncml.config import SyncMLConfigNode
from taskcoachlib.syncml.core import *

from taskcoachlib.i18n import _
from taskcoachlib.meta import data

import sys, wx


class AuthenticationFailure(Exception):
    pass


class TaskCoachManagementNode(ManagementNode):
    def __init__(self, syncMLConfig, *args, **kwargs):
        super(TaskCoachManagementNode, self).__init__(*args, **kwargs)

        self.__cfg = self.__getConfig(syncMLConfig)

    def __getConfig(self, cfg):
        for name in self.fullName.split("/"):
            for child in cfg.children():
                if child.name == name:
                    cfg = child
                    break
            else:
                child = SyncMLConfigNode(name)
                cfg.addChild(child)
                cfg = child

        return cfg

    def getChildrenMaxCount(self):
        return len(self.__cfg.children())

    def getChildrenNames(self):
        return [child.name for child in self.__cfg.children()]

    def readPropertyValue(self, name):
        return self.__cfg.get(name.decode("UTF-8")).encode("UTF-8")

    def setPropertyValue(self, name, value):
        self.__cfg.set(name.decode("UTF-8"), value.decode("UTF-8"))

    def clone(self):
        return self


class TaskCoachDMTree(DMTree):
    def __init__(self, syncMLConfig, *args, **kwargs):
        super(TaskCoachDMTree, self).__init__(*args, **kwargs)

        self.__syncMLConfig = syncMLConfig

    def isLeaf(self, node):
        return (
            TaskCoachManagementNode(
                self.__syncMLConfig, node
            ).getMaxChildrenCount()
            == 0
        )

    def readManagementNode(self, nodeName):
        node = TaskCoachManagementNode(self.__syncMLConfig, nodeName)

        for name in node.getChildrenNames():
            node.addChild(
                TaskCoachManagementNode(self.__syncMLConfig, nodeName, name)
            )

        return node


class TaskCoachDMTClientConfig(DMTClientConfig):
    def __init__(self, syncMLConfig, *args, **kwargs):
        super(TaskCoachDMTClientConfig, self).__init__(*args, **kwargs)

        self.__syncMLConfig = syncMLConfig

    def syncMLConfig(self):
        return self.__syncMLConfig

    def createDMTree(self, rootContext):
        return TaskCoachDMTree(self.__syncMLConfig, rootContext)


class Synchronizer(wx.ProgressDialog):
    def __init__(self, reportCallback, taskFile, password):
        super(Synchronizer, self).__init__(
            _("Synchronization"), _("Synchronizing. Please wait.\n\n\n")
        )

        self.clientName = "TaskCoach-%s" % taskFile.guid().encode("UTF-8")
        self.reportCallback = reportCallback
        self.taskFile = taskFile

        cfg = taskFile.syncMLConfig()

        self.username = (
            cfg[self.clientName]["spds"]["syncml"]["Auth"]
            .get("username")
            .encode("UTF-8")
        )  # Hum...
        self.password = password.encode("UTF-8")
        self.url = (
            cfg[self.clientName]["spds"]["syncml"]["Conn"]
            .get("syncUrl")
            .encode("UTF-8")
        )

        self.synctasks = (
            cfg[self.clientName]["spds"]["sources"][
                "%s.Tasks" % self.clientName
            ].get("dosync")
            == "True"
        )
        self.syncnotes = (
            cfg[self.clientName]["spds"]["sources"][
                "%s.Notes" % self.clientName
            ].get("dosync")
            == "True"
        )

        self.taskdbname = (
            cfg[self.clientName]["spds"]["sources"][
                "%s.Tasks" % self.clientName
            ]
            .get("uri")
            .encode("UTF-8")
        )
        self.notedbname = (
            cfg[self.clientName]["spds"]["sources"][
                "%s.Notes" % self.clientName
            ]
            .get("uri")
            .encode("UTF-8")
        )

        self.taskmode = cfg[self.clientName]["spds"]["sources"][
            "%s.Tasks" % self.clientName
        ].get("preferredsyncmode")
        self.notemode = cfg[self.clientName]["spds"]["sources"][
            "%s.Notes" % self.clientName
        ].get("preferredsyncmode")

    def init(self):
        self.dmt = TaskCoachDMTClientConfig(
            self.taskFile.syncMLConfig(), self.clientName
        )

        if not (
            self.dmt.read() and self.dmt.deviceConfig.devID == self.clientName
        ):
            self.dmt.setClientDefaults()

        ac = self.dmt.accessConfig
        ac.username = self.username
        ac.password = self.password

        ac.useProxy = 0
        ac.syncURL = self.url
        self.dmt.accessConfig = ac

        dc = self.dmt.deviceConfig
        dc.devID = self.clientName
        dc.devType = "workstation"
        dc.manufacturerName = "Task Coach developers"
        dc.modelName = sys.platform
        dc.firmwareVersion = "0.0"
        dc.softwareVersion = data.version
        self.dmt.deviceConfig = dc

        # Tasks source configuration

        self.sources = []

        if self.synctasks:
            try:
                cfg = self.dmt.getSyncSourceConfig(
                    "%s.Tasks" % self.clientName
                )
            except ValueError:
                cfg = SyncSourceConfig("%s.Tasks" % self.clientName)

            cfg.URI = self.taskdbname
            cfg.syncModes = "two-way"
            cfg.supportedTypes = "text/calendar"
            cfg.version = "1.0"

            self.dmt.setSyncSourceConfig(cfg)

            src = TaskSource(
                self,
                self.taskFile.tasks(),
                self.taskFile.categories(),
                "%s.Tasks" % self.clientName,
                cfg,
            )
            src.preferredSyncMode = globals()[self.taskmode]
            self.sources.append(src)

        if self.syncnotes:
            try:
                cfg = self.dmt.getSyncSourceConfig(
                    "%s.Notes" % self.clientName
                )
            except ValueError:
                cfg = SyncSourceConfig("%s.Notes" % self.clientName)

            cfg.URI = self.notedbname
            cfg.syncModes = "two-way"
            cfg.supportedTypes = "text/x-vnote:1.1"
            cfg.version = "1.0"

            self.dmt.setSyncSourceConfig(cfg)

            src = NoteSource(
                self,
                self.taskFile.notes(),
                self.taskFile.categories(),
                # This is ugly and doesn't work for every configuration but well...
                (
                    "text/plain"
                    if self.url.endswith("rpc.php")
                    else "text/x-vnote"
                ),
                "%s.Notes" % self.clientName,
                cfg,
            )
            src.preferredSyncMode = globals()[self.notemode]
            self.sources.append(src)

    def onAddItem(self):
        self.added += 1
        self.pulse()

    def onUpdateItem(self):
        self.updated += 1
        self.pulse()

    def onDeleteItem(self):
        self.deleted += 1
        self.pulse()

    def pulse(self):
        msg = _("%d items added.\n%d items updated.\n%d items deleted.") % (
            self.added,
            self.updated,
            self.deleted,
        )
        self.Pulse(msg)

    def error(self, code, msg):
        self.reportCallback(
            _(
                "An error occurred in the synchronization.\nError code: %d; message: %s"
            )
            % (code, msg)
        )

    def synchronize(self):
        if not self.username:
            self.reportCallback(
                _(
                    "You must first edit your SyncML Settings, in Edit/SyncML preferences."
                )
            )
            return False

        self.Centre()
        self.Show()

        self.added = 0
        self.updated = 0
        self.deleted = 0

        self.taskFile.beginSync()
        try:
            self.init()

            client = SyncClient()
            client.sync(self.dmt, self.sources)

            code = client.report.lastErrorCode

            if code:
                if code == 401:
                    raise AuthenticationFailure()
                self.error(code, client.report.lastErrorMsg)

                # TODO: undo local modifications ?
                return False

            self.dmt.save()
        finally:
            self.taskFile.setSyncMLConfig(self.dmt.syncMLConfig())
            self.taskFile.endSync()

        return True
