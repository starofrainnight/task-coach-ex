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

# taskcoachlib contains all taskcoach packages

# When thirdparty packages are imported, they may import submodules
# from the system-wide installation. Doing this in workaround/__init__.py is too late.
import os, sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "thirdparty"))
)
