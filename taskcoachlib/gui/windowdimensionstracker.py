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
from taskcoachlib import operating_system


class _Tracker(object):
    """Utility methods for setting and getting values from/to the
    settings."""

    def __init__(self, settings, section):
        super(_Tracker, self).__init__()
        self.__settings = settings
        self.__section = section

    def set_setting(self, setting, value):
        """Store the value for the setting in the settings."""
        self.__settings.setvalue(self.__section, setting, value)

    def get_setting(self, setting):
        """Get the value for the setting from the settings and return it."""
        return self.__settings.getvalue(self.__section, setting)


class WindowSizeAndPositionTracker(_Tracker):
    """Track the size and position of a window in the settings."""

    def __init__(self, window, settings, section):
        super(WindowSizeAndPositionTracker, self).__init__(settings, section)
        self._window = window
        self.__set_dimensions()
        self._window.Bind(wx.EVT_SIZE, self.on_change_size)
        self._window.Bind(wx.EVT_MOVE, self.on_change_position)
        self._window.Bind(wx.EVT_MAXIMIZE, self.on_maximize)

    def on_change_size(self, event):
        """Handle a size event by saving the new size of the window in the
        settings."""
        # Ignore the EVT_SIZE when the window is maximized or iconized.
        # Note how this depends on the EVT_MAXIMIZE being sent before the
        # EVT_SIZE.
        maximized = self._window.IsMaximized()
        if not maximized and not self._window.IsIconized():
            self.set_setting(
                "size",
                (
                    self._window.GetClientSize()
                    if operating_system.isMac()
                    else event.GetSize()
                ),
            )
        # Jerome, 2008/07/12: On my system (KDE 3.5.7), EVT_MAXIMIZE
        # is not triggered, so set 'maximized' to True here as well as in
        # onMaximize:
        self.set_setting("maximized", maximized)
        event.Skip()

    def on_change_position(self, event):
        """Handle a move event by saving the new position of the window in
        the settings."""
        if not self._window.IsMaximized():
            self.set_setting("maximized", False)
            if not self._window.IsIconized():
                # Only save position when the window is not maximized
                # *and* not minimized
                self.set_setting("position", event.GetPosition())
        event.Skip()

    def on_maximize(self, event):
        """Handle a maximize event by saving the window maximization state in
        the settings."""
        self.set_setting("maximized", True)
        event.Skip()

    def __set_dimensions(self):
        """Set the window position and size based on the settings."""
        x, y = self.get_setting("position")  # pylint: disable=C0103
        width, height = self.get_setting("size")
        if operating_system.isMac():
            # Under MacOS 10.5 and 10.4, when setting the size, the actual
            # window height is increased by 40 pixels. Dunno why, but it's
            # highly annoying. This doesn't hold for dialogs though. Sigh.
            if not isinstance(self._window, wx.Dialog):
                height += 18
        self._window.SetSize(x, y, width, height)
        if operating_system.isMac():
            self._window.SetClientSize((width, height))
        if self.get_setting("maximized"):
            self._window.Maximize()
        # Check that the window is on a valid display and move if necessary:
        if wx.Display.GetFromWindow(self._window) == wx.NOT_FOUND:
            # Not (0, 0) because on OSX this hides the window bar...
            self._window.SetDimensions(50, 50, width, height)
            if operating_system.isMac():
                self._window.SetClientSize((width, height))


class WindowDimensionsTracker(WindowSizeAndPositionTracker):
    """Track the dimensions of a window in the settings."""

    def __init__(self, window, settings):
        super(WindowDimensionsTracker, self).__init__(
            window, settings, "window"
        )
        self.__settings = settings
        if self.__start_iconized():
            if operating_system.isMac() or operating_system.isGTK():
                # Need to show the window on Mac OS X first, otherwise it
                # won't be properly minimized. On wxGTK we need to show the
                # window first, otherwise clicking the task bar icon won't
                # show it.
                self._window.Show()
            self._window.Iconize(True)
            if not operating_system.isMac() and self.get_setting(
                "hidewheniconized"
            ):
                # Seems like hiding the window after it's been
                # iconized actually closes it on Mac OS...
                wx.CallAfter(self._window.Hide)

    def __start_iconized(self):
        """Return whether the window should be opened iconized."""
        start_iconized = self.__settings.get("window", "starticonized")
        if start_iconized == "Always":
            return True
        if start_iconized == "Never":
            return False
        return self.get_setting("iconized")

    def save_position(self):
        """Save the position of the window in the settings."""
        iconized = self._window.IsIconized()
        self.set_setting("iconized", iconized)
        if not iconized:
            self.set_setting("position", self._window.GetPosition())
