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

import os, test

# Tests are run with ./tests as current dir, but setup.py expects the project
# root folder to be the current dir. Work around that by changing
# the current dir while importing setup.py:
cwd = os.path.realpath(os.path.curdir)
os.chdir("..")
import setup

os.chdir(cwd)


class LineEndingsTest(test.TestCase):
    def testNoDOSLineEndingsInPythonScripts(self):
        """On Linux, scripts won't work if they have DOS line endings."""
        scripts = [
            os.path.join(test.projectRoot, script)
            for script in setup.setupOptions["scripts"]
            if script.endswith(".py")
        ]
        for script in scripts:
            self.assertFalse(
                "\r\n" in open(script, "rb").read(),
                "%s contains DOS line endings" % script,
            )
