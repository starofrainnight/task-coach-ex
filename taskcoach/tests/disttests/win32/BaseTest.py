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

import os, time, base


class TestLaunch(base.Win32TestCase):
    def test_launch(self):
        window = self.findWindow(r"^Task Coach$")
        self.assertFalse(window is None, "Cannot find main window")


class TestWithTaskFile(base.Win32TestCase):
    def setUp(self):
        self.args = ['"%s"' % os.path.join(self.basepath, "testfile.tsk")]
        super(TestWithTaskFile, self).setUp()

    def test_launch(self):
        self.assertTrue(
            self.findWindow(r"^Task Coach file error$") is None,
            "Error dialog appeared",
        )
        window = self.findWindow(r"^Task Coach", tries=20)
        self.assertFalse(window is None, "Cannot find main window")
        self.assertTrue(
            window.title.endswith("testfile.tsk"), "Wrong window title"
        )

    def test_save(self):
        filename = self.args[0][1:-1]  # Remove "'s
        timestamp = os.stat(filename).st_mtime

        mainwindow = self.findWindow(r"^Task Coach", tries=20)
        w = mainwindow.findChildren("wxWindowClassNR", "HyperTreeList")

        # Double-click the first task to open the task edit dialog:
        for _ in range(2):
            w[1].clickAt(5, 30)
            time.sleep(0.1)

        editor = self.findWindow(r"\(task\)$")
        self.assertFalse(editor is None, "Task editor not found")
        editor.waitFocus()

        # Change subject so the task is "dirty":
        editor.sendText("New subject")
        # Close the task edit dialog:
        editor.close()

        mainwindow.waitFocus()
        mainwindow.clickAt(58, 15)  # Save button

        # Give some time to write the file...
        time.sleep(15)

        if os.path.exists(self.logfilename):
            self.fail(
                "Exception occurred while saving:\n"
                + open(self.logfilename, "rb").read()
            )

        # This fails for a yet unknown reason when launched through the buildbot. Seems
        # to work fine by hand...

        ## self.failUnless(os.stat(filename).st_mtime > timestamp,
        ##                 'File was not written')
        ## self.assertNotEqual(os.path.getsize(filename), 0)
