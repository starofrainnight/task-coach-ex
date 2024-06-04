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

import converter, changes, sys

numberOfReleases = int(sys.argv[2]) if len(sys.argv) >= 3 else sys.maxsize

if sys.argv[1] == "text":
    converter = converter.ReleaseToTextConverter()
elif sys.argv[1] == "html":
    converter = converter.ReleaseToHTMLConverter()
elif sys.argv[1] == "debian":
    # Only current release, Debian format
    converter = converter.ReleaseToDebianConverter()
    numberOfReleases = 1
else:
    raise ValueError("Unknown target format (%s)" % sys.argv[1])

releases = changes.releases[:numberOfReleases]
for release in releases:
    print(converter.convert(release))
