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

import test
from taskcoachlib import gui, config, persistence, operating_system
from taskcoachlib.domain import attachment


class DummyEvent(object):
    def Skip(self):  # pragma: no cover
        pass


class AttachmentEditorTest(test.wxTestCase):
    def setUp(self):
        super(AttachmentEditorTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.attachment = attachment.FileAttachment("Attachment")
        self.attachments = attachment.AttachmentList()
        self.attachments.append(self.attachment)
        self.editor = gui.dialog.editor.AttachmentEditor(
            self.frame,
            self.attachments,
            self.settings,
            self.attachments,
            self.taskFile,
        )

    def tearDown(self):
        super(AttachmentEditorTest, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()

    def setSubject(self, newSubject):
        page = self.editor._interior[0]
        page._subjectEntry.SetFocus()
        page._subjectEntry.SetValue(newSubject)
        if operating_system.isGTK():  # pragma: no cover
            page._subjectSync.onAttributeEdited(DummyEvent())
        else:  # pragma: no cover
            page._descriptionEntry.SetFocus()

    def setDescription(self, newDescription):
        page = self.editor._interior[0]
        page._descriptionEntry.SetFocus()
        page._descriptionEntry.SetValue(newDescription)
        if operating_system.isGTK():  # pragma: no cover
            page._descriptionSync.onAttributeEdited(DummyEvent())
        else:  # pragma: no cover
            page._subjectEntry.SetFocus()

    def testCreate(self):
        # pylint: disable=W0212
        self.assertEqual(
            "Attachment", self.editor._interior[0]._subjectEntry.GetValue()
        )

    def testEditSubject(self):
        self.setSubject("Done")
        self.assertEqual("Done", self.attachment.subject())

    def testEditDescription(self):
        self.setDescription("Description")
        self.assertEqual("Description", self.attachment.description())

    def testAddNote(self):
        viewer = self.editor._interior[1].viewer
        viewer.newItemCommand(viewer.presentation()).do()
        self.assertEqual(
            1, len(self.attachment.notes())
        )  # pylint: disable=E1101
