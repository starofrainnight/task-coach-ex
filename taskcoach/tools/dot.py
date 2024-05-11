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

import os, re, glob, sys

packages = []
modules = []
classdef = re.compile("class ([A-Za-z]+)\(([^)]+)\)", re.MULTILINE)


def stripmodule(classname):
    return classname.split(".")[-1]


print('digraph G {\nrankdir="LR"')

for filename in glob.glob(os.path.join(sys.argv[1], "*.py")):
    contents = open(filename).read()
    matches = classdef.findall(contents)
    if not matches:
        continue

    module = os.path.basename(filename)[: -len(".py")]
    print("subgraph cluster%s {" % module)
    print("label=%s" % module)
    print(" ".join([classes[0] for classes in matches]))
    print("}\n")
    for match in matches:
        class_ = stripmodule(match[0])
        superclasses = re.sub("\s", "", match[1]).split(",")
        for superclass in superclasses:
            if superclass == "object":
                continue
            print("%s->%s" % (stripmodule(superclass), class_))
    print()

print("}")
