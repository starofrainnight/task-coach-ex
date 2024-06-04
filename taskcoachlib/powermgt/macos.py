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

# When running from source, select the right binary...

import sys

if not hasattr(sys, "frozen"):
    import struct, os

    _subdir = "ia64" if struct.calcsize("L") == 8 else "ia32"

    sys.path.insert(
        0,
        os.path.join(
            os.path.split(__file__)[0],
            "..",
            "..",
            "extension",
            "macos",
            "bin-%s" % _subdir,
        ),
    )

import _powermgt  # pylint: disable=F0401
import threading
import wx
from taskcoachlib.powermgt.base import PowerStateMixinBase


class PowerStateMixin(PowerStateMixinBase):
    POWERON = _powermgt.POWERON
    POWEROFF = _powermgt.POWEROFF

    def __init__(self, *args, **kwargs):
        super(PowerStateMixin, self).__init__(*args, **kwargs)

        class Observer(_powermgt.PowerObserver):
            def __init__(self, cb):
                super(Observer, self).__init__()

                self.__callback = cb

            def PowerNotification(self, state):
                wx.CallAfter(self.__callback, state)

        self.__observer = Observer(self.__OnPowerState)
        self.__thread = threading.Thread(
            target=self.__observer.run
        )  # pylint: disable=E1101
        self.__thread.start()

    def __OnPowerState(self, state):
        self.OnPowerState(state)

    def OnQuit(self):
        self.__observer.stop()  # pylint: disable=E1101
        self.__thread.join()
