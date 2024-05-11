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

import glob, shutil, sys, os, urllib.request, urllib.parse, urllib.error, tarfile, glob

projectRoot = os.path.abspath("..")
if projectRoot not in sys.path:
    sys.path.insert(0, projectRoot)
from taskcoachlib.i18n import po2dict


def downloadTranslations(url):
    def po_files(members):
        for member in members:
            if os.path.splitext(member.name)[1] == ".po":
                yield member

    filename, info = urllib.request.urlretrieve(url)
    tarFile = tarfile.open(filename, "r:gz")
    folder = [member for member in tarFile if member.isdir()][0].name
    tarFile.extractall(members=po_files(tarFile))
    tarFile.close()
    os.remove(filename)

    for poFile in glob.glob("*.po"):
        newPoFile = os.path.join(folder, "i18n.in-%s" % poFile)
        shutil.copy(newPoFile, poFile)
        print("Updating", poFile)
    shutil.rmtree(folder)


def downloadTranslation(url):
    # http://launchpadlibrarian.net/70943850/i18n.in_i18n.in-nl.po
    filename, info = urllib.request.urlretrieve(url)
    shutil.move(filename, url.split("-")[1])


def createPoDicts():
    for poFile in sorted(glob.glob("*.po")):
        print("Creating python dictionary from", poFile)
        pyFile = po2dict.make(poFile)
        shutil.move(pyFile, "../taskcoachlib/i18n/%s" % pyFile)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        url = sys.argv[1]
        if url.endswith(".po"):
            downloadTranslation(url)
        else:
            downloadTranslations(url)
    else:
        createPoDicts()
