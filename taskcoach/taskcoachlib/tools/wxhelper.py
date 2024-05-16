# -*- coding: utf-8 -*-

from typing import Union
import wx


def getButtonFromStdDialogButtonSizer(
    sizer: wx.StdDialogButtonSizer, buttonId: int
) -> Union[wx.Button, None]:
    for child in sizer.GetChildren():
        if (
            isinstance(child.GetWindow(), wx.Button)
            and child.GetWindow().GetId() == buttonId
        ):
            return child.GetWindow()

    return None
