"""
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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

import sys, time, wx
from taskcoachlib import operating_system
from ctypes import *


# ==============================================================================
# Linux/BSD

if operating_system.isGTK():

    class XScreenSaverInfo(Structure):
        _fields_ = [
            ("window", c_ulong),
            ("state", c_int),
            ("kind", c_int),
            ("til_or_since", c_ulong),
            ("idle", c_ulong),
            ("event_mask", c_ulong),
        ]

    class LinuxIdleQuery(object):
        def __init__(self):
            _x11 = CDLL("libX11.so.6")

            self.XOpenDisplay = CFUNCTYPE(c_ulong, c_char_p)(
                ("XOpenDisplay", _x11)
            )
            self.XCloseDisplay = CFUNCTYPE(c_int, c_ulong)(
                ("XCloseDisplay", _x11)
            )
            self.XRootWindow = CFUNCTYPE(c_ulong, c_ulong, c_int)(
                ("XRootWindow", _x11)
            )

            self.dpy = self.XOpenDisplay(None)

            _xss = CDLL("libXss.so.1")

            self.XScreenSaverAllocInfo = CFUNCTYPE(POINTER(XScreenSaverInfo))(
                ("XScreenSaverAllocInfo", _xss)
            )
            self.XScreenSaverQueryInfo = CFUNCTYPE(
                c_int, c_ulong, c_ulong, POINTER(XScreenSaverInfo)
            )(("XScreenSaverQueryInfo", _xss))

            self.info = self.XScreenSaverAllocInfo()

        def __del__(self):
            self.XCloseDisplay(self.dpy)

        def getIdleSeconds(self):
            self.XScreenSaverQueryInfo(
                self.dpy, self.XRootWindow(self.dpy, 0), self.info
            )
            return 1.0 * self.info.contents.idle / 1000

    IdleQuery = LinuxIdleQuery

elif operating_system.isWindows():

    class LASTINPUTINFO(Structure):
        _fields_ = [("cbSize", c_uint), ("dwTime", c_uint)]

    class WindowsIdleQuery(object):
        def __init__(self):
            self.GetTickCount = windll.kernel32.GetTickCount
            self.GetLastInputInfo = windll.user32.GetLastInputInfo

            self.lastInputInfo = LASTINPUTINFO()
            self.lastInputInfo.cbSize = sizeof(self.lastInputInfo)

        def getIdleSeconds(self):
            self.GetLastInputInfo(byref(self.lastInputInfo))
            return (
                1.0 * self.GetTickCount() - self.lastInputInfo.dwTime
            ) / 1000

    IdleQuery = WindowsIdleQuery

elif operating_system.isMac():
    # When running from source, select the right binary...

    if not hasattr(sys, "frozen"):
        import struct, os

        if struct.calcsize("L") == 8:
            _subdir = "ia64"
        else:
            _subdir = "ia32"

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

    import _idle

    class MacIdleQuery(_idle.Idle):
        def getIdleSeconds(self):
            return self.get()

    IdleQuery = MacIdleQuery


# ==============================================================================
#


class IdleNotifier(wx.EvtHandler, IdleQuery):
    STATE_SLEEPING = 0
    STATE_AWAKE = 1

    def __init__(self):
        wx.EvtHandler.__init__(self)
        IdleQuery.__init__(self)

        self.state = self.STATE_AWAKE
        self.lastActivity = time.time()
        self.goneToSleep = None

        self._bound = True
        wx.GetApp().Bind(wx.EVT_IDLE, self._OnIdle)

    def stop(self):
        self.pause()

    def pause(self):
        if self._bound:
            wx.GetApp().Unbind(wx.EVT_IDLE, handler=self._OnIdle)
            self._bound = False

    def resume(self):
        self.state = self.STATE_AWAKE
        self.lastActivity = time.time()
        if not self._bound:
            wx.GetApp().Bind(wx.EVT_IDLE, self._OnIdle)

    def _check(self):
        if (
            self.state == self.STATE_AWAKE
            and time.time() - self.lastActivity >= self.getMinIdleTime()
        ):
            self.goneToSleep = self.lastActivity
            self.state = self.STATE_SLEEPING
            self.sleep()
        elif (
            self.state == self.STATE_SLEEPING
            and time.time() - self.lastActivity < self.getMinIdleTime()
        ):
            self.state = self.STATE_AWAKE
            self.wake(self.goneToSleep)

    def _OnIdle(self, event):
        self._check()
        self.lastActivity = time.time() - self.getIdleSeconds()
        self._check()
        event.Skip()

    def poweroff(self):
        """
        Call this when the computer goes to sleep.
        """
        if self._bound:
            wx.GetApp().Unbind(wx.EVT_IDLE, handler=self._OnIdle)
            self._bound = False

    def poweron(self):
        """
        Call this when the computer resumes from sleep.
        """
        if not self._bound:
            wx.GetApp().Bind(wx.EVT_IDLE, self._OnIdle)
            self._bound = True
        self._check()
        self.lastActivity = time.time() - self.getIdleSeconds()
        self._check()

    def getMinIdleTime(self):
        """
        Should return the minimum time in seconds before going idle.
        """
        raise NotImplementedError

    def sleep(self):
        """
        Called when the min idle time has elapsed without any user
        input.
        """

    def wake(self, timestamp):
        """
        Called when the computer is not idle any more.
        """
