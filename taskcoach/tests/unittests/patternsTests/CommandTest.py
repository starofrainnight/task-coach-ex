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
from unittests import asserts
from taskcoachlib import patterns


class HistoryTest(test.TestCase, asserts.CommandAssertsMixin):
    def setUp(self):
        self.commands = patterns.CommandHistory()
        self.command = patterns.Command()

    def tearDown(self):
        self.commands.clear()

    def testSingleton(self):
        another = patterns.CommandHistory()
        self.assertTrue(self.commands is another)

    def testClear(self):
        self.command.do()
        self.commands.clear()
        self.assertHistoryAndFuture([], [])

    def testDo(self):
        self.command.do()
        self.assertHistoryAndFuture([self.command], [])

    def testUndo(self):
        self.command.do()
        self.commands.undo()
        self.assertHistoryAndFuture([], [self.command])

    def testRedo(self):
        self.command.do()
        self.commands.undo()
        self.commands.redo()
        self.assertHistoryAndFuture([self.command], [])

    def testUndoStr_EmptyHistory(self):
        self.assertEqual("Undo", self.commands.undostr())

    def testUndoStr(self):
        self.command.do()
        self.assertEqual("Undo %s" % self.command, self.commands.undostr())

    def testRedoStr_EmptyFuture(self):
        self.assertEqual("Redo", self.commands.redostr())

    def testRedoStr(self):
        self.command.do()
        self.commands.undo()
        self.assertEqual("Redo %s" % self.command, self.commands.redostr())

    def testHasHistory(self):
        self.assertFalse(self.commands.hasHistory())
        self.command.do()
        self.assertTrue(self.commands.hasHistory())
        self.commands.undo()
        self.assertFalse(self.commands.hasHistory())

    def testHasFuture(self):
        self.command.do()
        self.assertFalse(self.commands.hasFuture())
        self.commands.undo()
        self.assertTrue(self.commands.hasFuture())
        self.commands.redo()
        self.assertFalse(self.commands.hasFuture())
