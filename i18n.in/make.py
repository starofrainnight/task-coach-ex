'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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
'''

import glob, shutil, sys, os
projectRoot = os.path.abspath('..')
if projectRoot not in sys.path:
    sys.path.insert(0, projectRoot)
from taskcoachlib.i18n import po2dict 


for poFile in sorted(glob.glob('*.po')):
    print 'Creating python dictionary from', poFile
    pyFile = po2dict.make(poFile)
    shutil.move(pyFile, '../taskcoachlib/i18n/%s'%pyFile)