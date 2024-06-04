#!/usr/bin/python

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

import os, re, sys


def findLatest(path, valid):
    rx = re.compile(r"(.*)(\d+\.\d+\.\d+\.\d+)(.*)")

    results = dict()

    for name in os.listdir(path):
        if name.lower().startswith("taskcoach") and valid(name):
            mt = rx.search(name)
            if mt:
                ls = results.get((mt.group(1), mt.group(3)), [])
                ls.append(list(map(int, mt.group(2).split("."))))
                results[(mt.group(1), mt.group(3))] = ls

    packages = []

    for (part1, part3), versions in list(results.items()):
        versions.sort()
        packages.append(
            "%s%s%s" % (part1, ".".join(map(str, versions[-1])), part3)
        )

    packages.sort()

    return packages


def listPath(path):
    def isSource(name):
        return (
            name.endswith(".zip")
            or name.endswith(".tar.gz")
            or name.endswith(".src.rpm")
        )

    print("<h2>Sources</h2>")
    print("<ul>")

    for pkgname in findLatest(path, isSource):
        if path == "." or path == "all":
            print(
                '<li><a href="http://jeromelaheurte.net/TaskCoach-packages/%s">%s</a></li>'
                % (pkgname, pkgname)
            )
        else:
            print(
                '<li><a href="http://jeromelaheurte.net/TaskCoach-packages/%s/%s">%s</a></li>'
                % (path, pkgname, pkgname)
            )

    print("</ul>")

    print("<h2>Binaries</h2>")
    print("<ul>")

    for pkgname in findLatest(path, lambda x: not isSource(x)):
        if path == "." or path == "all":
            print(
                '<li><a href="http://jeromelaheurte.net/TaskCoach-packages/%s">%s</a></li>'
                % (pkgname, pkgname)
            )
        else:
            print(
                '<li><a href="http://jeromelaheurte.net/TaskCoach-packages/%s/%s">%s</a></li>'
                % (path, pkgname, pkgname)
            )

    print("</ul>")


def main(path):
    print("Content-type: text/html")
    print()

    print("<html><head><title>Latest Task Coach builds</title>")
    print(
        '<style type="text/css" media="screen">@import "default.css";</style>'
    )
    print("</head></body>")

    if path == "." or path == "all":
        print("<h1>New developments (from trunk)</h1>")
        listPath(".")

    if path != ".":
        for name in os.listdir(path):
            if name.startswith("Release"):
                fname = os.path.join(path, name)
                if os.path.isdir(fname):
                    print("<h1>Bug fixes (from %s)</h1>" % name)
                    listPath(fname)

    print(
        '<a href="http://www.taskcoach.org/download.html>Back to Task Coach downloads</a>'
    )

    print("</body></html>")


if __name__ == "__main__":
    if sys.argv[0].endswith("latest_features.py"):
        main(".")
    elif sys.argv[0].endswith("latest_bugfixes.py"):
        main("branches")
    else:
        main("all")
