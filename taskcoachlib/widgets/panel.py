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


class PanelWithBoxSizer(wx.Panel):
    def __init__(self, *args, **kwargs):
        orientation = kwargs.pop("orientation", wx.VERTICAL)
        super(PanelWithBoxSizer, self).__init__(*args, **kwargs)
        self.__panelSizer = wx.BoxSizer(orientation)

    def fit(self):
        """Call this method after all controls have been added (via add())."""
        self.SetSizerAndFit(self.__panelSizer)

    def add(self, *args, **kwargs):
        defaultKwArgs = dict(flag=wx.EXPAND | wx.ALL, proportion=1)
        defaultKwArgs.update(kwargs)
        self.__panelSizer.Add(*args, **defaultKwArgs)


class BoxWithFlexGridSizer(wx.Panel):
    """A panel that is boxed and has a FlexGridSizer inside it."""

    def __init__(
        self,
        parent,
        label,
        cols,
        gap=10,
        vgap=0,
        hgap=0,
        growableRow=-1,
        growableCol=-1,
        *args,
        **kwargs
    ):
        super(BoxWithFlexGridSizer, self).__init__(parent, *args, **kwargs)
        box = wx.StaticBox(self, label=label)
        self.__boxSizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.__entriesSizer = wx.FlexGridSizer(
            cols=cols, vgap=gap or vgap, hgap=gap or hgap
        )
        if growableRow > -1:
            self.__entriesSizer.AddGrowableRow(growableRow, proportion=1)
        if growableCol > -1:
            self.__entriesSizer.AddGrowableCol(growableCol, proportion=1)
        self.__boxSizer.Add(
            self.__entriesSizer,
            proportion=1,
            flag=wx.EXPAND | wx.ALL,
            border=10,
        )

    def fit(self):
        """Call this method after all controls have been added (via add())."""
        self.SetSizerAndFit(self.__boxSizer)

    def add(self, control, *args, **kwargs):
        """Add controls to the FlexGridSizer."""
        if type(control) in (type(""), type("")):
            control = wx.StaticText(self, label=control)
            if "flag" not in kwargs:
                kwargs["flag"] = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL
        self.__entriesSizer.Add(control, *args, **kwargs)


class BoxWithBoxSizer(wx.Panel):
    """A panel that is boxed and has a BoxSizer inside it."""

    def __init__(
        self, parent, label, orientation=wx.VERTICAL, *args, **kwargs
    ):
        super(BoxWithBoxSizer, self).__init__(parent, *args, **kwargs)
        box = wx.StaticBox(self, label=label)
        self.__boxSizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.__innerBoxSizer = wx.BoxSizer(orientation)
        self.__boxSizer.Add(
            self.__innerBoxSizer,
            proportion=1,
            flag=wx.EXPAND | wx.ALL,
            border=10,
        )

    def fit(self):
        """Call this method after all controls have been added (via add())."""
        self.SetSizerAndFit(self.__boxSizer)

    def add(self, control, *args, **kwargs):
        """Add controls to the BoxSizer."""
        self.__innerBoxSizer.Add(control, *args, **kwargs)
