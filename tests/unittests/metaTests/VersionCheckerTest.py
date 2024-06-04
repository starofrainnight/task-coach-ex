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
from taskcoachlib import config, meta


class VersionCheckerUnderTest(meta.VersionChecker):
    def __init__(self, *args, **kwargs):
        self.version = kwargs.pop("version")
        self.retrievalException = kwargs.pop("retrievalException", None)
        self.parseException = kwargs.pop("parseException", None)
        self.userNotified = False
        super(VersionCheckerUnderTest, self).__init__(*args, **kwargs)

    def retrieveVersionFile(self):  # pylint: disable=W0221
        if self.retrievalException:
            raise self.retrievalException
        else:
            import io

            return io.StringIO("%s\n" % self.version)

    def parseVersionFile(self, versionFile):  # pylint: disable=W0221
        if self.parseException:
            raise self.parseException
        else:
            return super(VersionCheckerUnderTest, self).parseVersionFile(
                versionFile
            )

    def notifyUser(self, *args, **kwargs):  # pylint: disable=W0221,W0613
        self.userNotified = True


class VersionCheckerTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)

    def checkVersion(
        self, version, retrievalException=None, parseException=None
    ):
        checker = VersionCheckerUnderTest(
            self.settings,
            version=version,
            retrievalException=retrievalException,
            parseException=parseException,
        )
        checker.run()
        return checker

    def assertLastVersionNotified(
        self, version, retrievalException=None, parseException=None
    ):
        self.checkVersion(version, retrievalException, parseException)
        self.assertEqual(version, self.settings.get("version", "notified"))

    def testLatestVersionIsNewerThanLastVersionNotified(self):
        self.assertLastVersionNotified("99.99.99")

    def testLatestVersionEqualsLastVersionNotified(self):
        self.assertLastVersionNotified(meta.data.version)

    def testErrorWhileGettingPadFile(self):
        import urllib.request, urllib.error, urllib.parse

        retrievalException = urllib.error.HTTPError(
            None, None, None, None, None
        )
        self.assertLastVersionNotified(meta.data.version, retrievalException)

    def testExpatParsingError(self):
        import xml.parsers.expat as expat

        exception = expat.error
        self.assertLastVersionNotified(
            meta.data.version, parseException=exception
        )

    def testDontNotifyWhenCurrentVersionIsNewerThanLastVersionNotified(self):
        self.settings.set("version", "notified", "0.0")
        checker = self.checkVersion(meta.data.version)
        self.assertFalse(checker.userNotified)

    def test9IsNotNewerThan10(self):
        currentVersion = meta.data.version
        meta.data.version = "0.72.10"
        self.settings.set("version", "notified", "0.72.8")
        checker = self.checkVersion("0.72.9")
        self.assertFalse(checker.userNotified)
        meta.data.version = currentVersion

    def testShowDialog(self):
        class DummyDialog(object):
            def __init__(self, *args, **kwargs):  # pylint: disable=W0613
                self.shown = False

            def Show(self):
                self.shown = True

        checker = meta.VersionChecker(self.settings)
        dialog = checker.showDialog(DummyDialog, "1.0")
        self.assertTrue(dialog.shown)
