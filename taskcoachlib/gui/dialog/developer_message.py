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

from taskcoachlib.tools import wxhelper
import wx
from wx.lib.agw import hyperlink
from taskcoachlib import meta
from taskcoachlib.i18n import _
from wx.lib import sized_controls


class MessageDialog(sized_controls.SizedDialog):  # pylint: disable=R0904,R0901
    """Dialog for showing messages from the developers."""

    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop("settings")
        self.__message = kwargs.pop("message")
        self.__url = kwargs.pop("url")
        super(MessageDialog, self).__init__(
            title=_("Message from the %s " "developers") % meta.data.name,
            *args,
            **kwargs
        )
        pane = self.GetContentsPane()
        pane.SetSizerType("vertical")
        self.__create_message(pane)
        button_sizer = self.CreateStdDialogButtonSizer(wx.OK)
        self.SetButtonSizer(button_sizer)
        self.Fit()
        self.CentreOnParent()

        wxhelper.getButtonFromStdDialogButtonSizer(
            button_sizer, wx.ID_OK
        ).Bind(wx.EVT_BUTTON, self.on_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def __create_message(self, pane):
        """Create the interior parts of the dialog, i.e. the message for the
        user."""
        message = wx.StaticText(pane, label=self.__message)
        message.Wrap(500)
        url_panel = sized_controls.SizedPanel(pane)
        url_panel.SetSizerType("horizontal")
        wx.StaticText(url_panel, label=_("See:"))
        hyperlink.HyperLinkCtrl(url_panel, label=self.__url)

    def current_message(self):
        """Return the currently displayed message."""
        return self.__message

    def current_url(self):
        """Return the currently displayed url."""
        return self.__url

    def on_close(self, event):
        """When the user closes the dialog, remember what the last displayed
        message was."""
        event.Skip()
        self.__settings.settext("view", "lastdevelopermessage", self.__message)
