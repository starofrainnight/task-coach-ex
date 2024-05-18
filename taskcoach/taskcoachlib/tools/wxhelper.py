# -*- coding: utf-8 -*-

from typing import Union, List
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


def getAlphaDataFromImage(image: wx.Image) -> List[int]:
    data = []
    for y in range(0, image.Height):
        for x in range(0, image.Width):
            data.append(image.GetAlpha(x, y))

    return data


def setAlphaDataToImage(image: wx.Image, data: List[int]):
    for y in range(0, image.Height):
        for x in range(0, image.Width):
            image.SetAlpha(x, y, data[y * image.Width + x])


def clearAlphaDataOfImage(image: wx.Image, value: int):
    for y in range(0, image.Height):
        for x in range(0, image.Width):
            image.SetAlpha(x, y, value)
