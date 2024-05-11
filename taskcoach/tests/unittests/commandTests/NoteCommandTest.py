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

from unittests import asserts
from .CommandTestCase import CommandTestCase
from taskcoachlib import command, patterns
from taskcoachlib.domain import base, note, category, task


class NoteOwnerUnderTest(note.NoteOwner, base.Object):
    pass


class NoteCommandTestCase(CommandTestCase, asserts.CommandAssertsMixin):
    def setUp(self):
        self.notes = note.NoteContainer()
        self.taskList = task.TaskList()


class NewNoteCommandTest(NoteCommandTestCase):
    def new(self, categories=None):
        newNoteCommand = command.NewNoteCommand(
            self.notes, categories=categories or []
        )
        newNote = newNoteCommand.items[0]
        newNoteCommand.do()
        return newNote

    def testNewNote(self):
        newNote = self.new()
        self.assertDoUndoRedo(
            lambda: self.assertEqual([newNote], self.notes),
            lambda: self.assertEqual([], self.notes),
        )

    def testNewNoteWithCategory(self):
        cat = category.Category("cat")
        newNote = self.new(categories=[cat])
        self.assertDoUndoRedo(
            lambda: self.assertEqual(set([cat]), newNote.categories()),
            lambda: self.assertEqual([], self.notes),
        )


class AddNoteCommandTest(NoteCommandTestCase):
    def testAddedNoteIsRootItem(self):
        owner = NoteOwnerUnderTest()
        command.AddNoteCommand([owner], [owner]).do()
        self.assertTrue(
            owner.notes()[0].parent() is None
        )  # pylint: disable=E1101


class NewSubNoteCommandTest(NoteCommandTestCase):
    def setUp(self):
        super(NewSubNoteCommandTest, self).setUp()
        self.note = note.Note(subject="Note")
        self.notes.append(self.note)

    def newSubNote(self, notes=None):
        newSubNote = command.NewSubNoteCommand(self.notes, notes or [])
        newSubNote.do()

    def testNewSubNote_WithoutSelection(self):
        self.newSubNote()
        self.assertDoUndoRedo(
            lambda: self.assertEqual([self.note], self.notes)
        )

    def testNewSubNote(self):
        self.newSubNote([self.note])
        newSubNote = self.note.children()[0]
        self.assertDoUndoRedo(
            lambda: self.assertEqual([newSubNote], self.note.children()),
            lambda: self.assertEqual([self.note], self.notes),
        )


class DragAndDropNoteCommand(NoteCommandTestCase):
    def setUp(self):
        super(DragAndDropNoteCommand, self).setUp()
        self.parent = note.Note(subject="parent")
        self.child = note.Note(subject="child")
        self.grandchild = note.Note(subject="grandchild")
        self.parent.addChild(self.child)
        self.child.addChild(self.grandchild)
        self.notes.extend([self.parent])

    def dragAndDrop(self, dropTarget, notes=None):
        command.DragAndDropNoteCommand(
            self.notes, notes or [], drop=dropTarget
        ).do()

    def testCannotDropOnParent(self):
        self.dragAndDrop([self.parent], [self.child])
        self.assertFalse(patterns.CommandHistory().hasHistory())

    def testCannotDropOnChild(self):
        self.dragAndDrop([self.child], [self.parent])
        self.assertFalse(patterns.CommandHistory().hasHistory())

    def testCannotDropOnGrandchild(self):
        self.dragAndDrop([self.grandchild], [self.parent])
        self.assertFalse(patterns.CommandHistory().hasHistory())

    def testDropAsRootTask(self):
        self.dragAndDrop([], [self.grandchild])
        self.assertDoUndoRedo(
            lambda: self.assertEqual(None, self.grandchild.parent()),
            lambda: self.assertEqual(self.child, self.grandchild.parent()),
        )
