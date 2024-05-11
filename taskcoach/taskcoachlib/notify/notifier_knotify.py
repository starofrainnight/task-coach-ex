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

import wx

from .notifier import AbstractNotifier


class KNotifyNotifier(AbstractNotifier):
    def __init__(self):
        super(KNotifyNotifier, self).__init__()

        self.__factory = None
        try:
            import pcop
            import pydcop
        except ImportError:
            pass
        else:
            if pydcop.anyAppCalled("knotify") is not None:
                self.__factory = pydcop.anyAppCalled

    def getName(self):
        return "KNotify"

    def isAvailable(self):
        return self.__factory is not None

    def notify(self, title, summary, bitmap, **kwargs):
        # KNotify does not support icons

        coding = wx.Locale_GetSystemEncodingName()

        kn = self.__factory("knotify")
        kn.default.notify(
            "reminder",
            title.encode(coding),
            summary.encode(coding),
            "",
            "",
            16,
            0,
            kwargs.get("windowId", 0),
        )


AbstractNotifier.register(KNotifyNotifier())
