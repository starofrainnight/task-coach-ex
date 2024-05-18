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

from taskcoachlib import patterns, operating_system
from taskcoachlib.i18n import _
from taskcoachlib.tools import wxhelper
import wx
from . import icons


class ArtProvider(wx.ArtProvider):
    def CreateBitmap(self, artId, artClient, size):
        if "+" in artId:
            w, h = size
            main, overlay = artId.split("+")

            overlayImage = self._CreateBitmap(
                overlay, artClient, size
            ).ConvertToImage()  # type: wx.Image
            overlayImage.Rescale(int(w / 2), int(h / 2), wx.IMAGE_QUALITY_HIGH)

            overlayAlpha = overlayImage.GetAlphaBuffer()
            overlayBitmap = overlayImage.ConvertToBitmap()

            mainImage = self._CreateBitmap(
                main, artClient, size
            ).ConvertToImage()  # type: wx.Image
            mainAlpha = wxhelper.getAlphaDataFromImage(mainImage)
            wxhelper.clearAlphaDataOfImage(mainImage, 255)
            mainBitmap = mainImage.ConvertToBitmap()

            dstDC = wx.MemoryDC()
            dstDC.SelectObject(mainBitmap)
            try:
                dstDC.DrawBitmap(
                    overlayBitmap, w - (w // 2), h - (h // 2), True
                )
            finally:
                dstDC.SelectObject(wx.NullBitmap)
            mainImage = mainBitmap.ConvertToImage()

            # Just drawing works fine on OS X but clips to the destination bitmap on
            # other platforms. There doesn't seem to be anything better than this.
            resultAlpha = list()
            for y in range(h):
                for x in range(w):
                    alpha = mainAlpha[y * w + x]
                    if x >= w // 2 and y >= h // 2:
                        alpha = max(
                            alpha,
                            overlayAlpha[(y - h // 2) * w // 2 + x - w // 2],
                        )
                    resultAlpha.append(alpha)
            wxhelper.setAlphaDataToImage(mainImage, resultAlpha)

            return mainImage.ConvertToBitmap()
        else:
            return self._CreateBitmap(artId, artClient, size)

    def _CreateBitmap(self, artId, artClient, size) -> wx.Bitmap:
        if not artId:
            return wx.Bitmap(*size)
        catalogKey = "%s%dx%d" % (artId, size[0], size[1])
        if catalogKey in list(icons.catalog.keys()):
            bitmap = icons.catalog[catalogKey].GetBitmap()
            if artClient == wx.ART_FRAME_ICON:
                bitmap = self.convertAlphaToMask(bitmap)
            return bitmap
        else:
            return wx.NullBitmap

    @staticmethod
    def convertAlphaToMask(bitmap):
        image = wx.ImageFromBitmap(bitmap)
        image.ConvertAlphaToMask()
        return wx.BitmapFromImage(image)


class IconProvider(object, metaclass=patterns.Singleton):
    def __init__(self):
        self.__iconCache = dict()
        if operating_system.isMac():
            self.__iconSizeOnCurrentPlatform = 128
        elif operating_system.isGTK():
            self.__iconSizeOnCurrentPlatform = 48
        else:
            self.__iconSizeOnCurrentPlatform = 16

    def getIcon(self, iconTitle):
        """Return the icon. Use a cache to prevent leakage of GDI object
        count."""
        try:
            return self.__iconCache[iconTitle]
        except KeyError:
            icon = self.getIconFromArtProvider(iconTitle)
            self.__iconCache[iconTitle] = icon
            return icon

    def iconBundle(self, iconTitle):
        """Create an icon bundle with icons of different sizes."""
        bundle = wx.IconBundle()
        for size in (16, 22, 32, 48, 64, 128):
            bundle.AddIcon(self.getIconFromArtProvider(iconTitle, size))
        return bundle

    def getIconFromArtProvider(self, iconTitle, iconSize=None):
        size = iconSize or self.__iconSizeOnCurrentPlatform
        # I just spent two hours trying to get rid of garbage in the icon
        # background on KDE. I give up.
        if operating_system.isGTK():
            return wx.ArtProvider.GetIcon(
                iconTitle, wx.ART_FRAME_ICON, (size, size)
            )

        # wx.ArtProvider.GetIcon doesn't convert alpha to mask, so we do it
        # ourselves:
        bitmap = wx.ArtProvider.GetBitmap(
            iconTitle, wx.ART_FRAME_ICON, (size, size)
        )
        bitmap = ArtProvider.convertAlphaToMask(bitmap)
        return wx.IconFromBitmap(bitmap)


def iconBundle(iconTitle):
    return IconProvider().iconBundle(iconTitle)


def getIcon(iconTitle):
    return IconProvider().getIcon(iconTitle)


def init():
    if operating_system.isWindows() and wx.DisplayDepth() >= 32:
        wx.SystemOptions_SetOption("msw.remap", "0")  # pragma: no cover
    try:
        wx.ArtProvider.PushProvider(ArtProvider())  # pylint: disable=E1101
    except AttributeError:
        wx.ArtProvider.Push(ArtProvider())


chooseableItemImages = dict(
    arrow_down_icon=_("Arrow down"),
    arrow_down_with_status_icon=_("Arrow down with status"),
    arrows_looped_blue_icon=_("Blue arrows looped"),
    arrows_looped_green_icon=_("Green arrows looped"),
    arrow_up_icon=_("Arrow up"),
    arrow_up_with_status_icon=_("Arrow up with status"),
    bomb_icon=_("Bomb"),
    book_icon=_("Book"),
    books_icon=_("Books"),
    box_icon=_("Box"),
    bug_icon=_("Ladybug"),
    cake_icon=_("Cake"),
    calculator_icon=_("Calculator"),
    calendar_icon=_("Calendar"),
    cat_icon=_("Cat"),
    cd_icon=_("Compact disc (CD)"),
    charts_icon=_("Charts"),
    chat_icon=_("Chatting"),
    checkmark_green_icon=_("Check mark"),
    checkmark_green_icon_multiple=_("Check marks"),
    clock_icon=_("Clock"),
    clock_alarm_icon=_("Alarm clock"),
    clock_stopwatch_icon=_("Stopwatch"),
    cogwheel_icon=_("Cogwheel"),
    cogwheels_icon=_("Cogwheels"),
    computer_desktop_icon=_("Desktop computer"),
    computer_laptop_icon=_("Laptop computer"),
    computer_handheld_icon=_("Handheld computer"),
    cross_red_icon=_("Red cross"),
    die_icon=_("Die"),
    document_icon=_("Document"),
    earth_blue_icon=_("Blue earth"),
    earth_green_icon=_("Green earth"),
    envelope_icon=_("Envelope"),
    envelopes_icon=_("Envelopes"),
    folder_blue_icon=_("Blue folder"),
    folder_blue_light_icon=_("Light blue folder"),
    folder_green_icon=_("Green folder"),
    folder_grey_icon=_("Grey folder"),
    folder_orange_icon=_("Orange folder"),
    folder_purple_icon=_("Purple folder"),
    folder_red_icon=_("Red folder"),
    folder_yellow_icon=_("Yellow folder"),
    folder_blue_arrow_icon=_("Blue folder with arrow"),
    heart_icon=_("Heart"),
    hearts_icon=_("Hearts"),
    house_green_icon=_("Green house"),
    house_red_icon=_("Red house"),
    key_icon=_("Key"),
    keys_icon=_("Keys"),
    lamp_icon=_("Lamp"),
    led_blue_questionmark_icon=_("Question mark"),
    led_blue_information_icon=_("Information"),
    led_blue_icon=_("Blue led"),
    led_blue_light_icon=_("Light blue led"),
    led_grey_icon=_("Grey led"),
    led_green_icon=_("Green led"),
    led_green_light_icon=_("Light green led"),
    led_orange_icon=_("Orange led"),
    led_purple_icon=_("Purple led"),
    led_red_icon=_("Red led"),
    led_yellow_icon=_("Yellow led"),
    life_ring_icon=_("Life ring"),
    lock_locked_icon=_("Locked lock"),
    lock_unlocked_icon=_("Unlocked lock"),
    magnifier_glass_icon=_("Magnifier glass"),
    music_piano_icon=_("Piano"),
    music_note_icon=_("Music note"),
    note_icon=_("Note"),
    palette_icon=_("Palette"),
    paperclip_icon=_("Paperclip"),
    pencil_icon=_("Pencil"),
    person_icon=_("Person"),
    persons_icon=_("People"),
    person_id_icon=_("Identification"),
    person_talking_icon=_("Person talking"),
    sign_warning_icon=_("Warning sign"),
    symbol_minus_icon=_("Minus"),
    symbol_plus_icon=_("Plus"),
    star_red_icon=_("Red star"),
    star_yellow_icon=_("Yellow star"),
    trafficlight_icon=_("Traffic light"),
    trashcan_icon=_("Trashcan"),
    weather_lightning_icon=_("Lightning"),
    weather_umbrella_icon=_("Umbrella"),
    weather_sunny_icon=_("Partly sunny"),
    wrench_icon=_("Wrench"),
)

itemImages = list(chooseableItemImages.keys()) + [
    "folder_blue_open_icon",
    "folder_green_open_icon",
    "folder_grey_open_icon",
    "folder_orange_open_icon",
    "folder_red_open_icon",
    "folder_purple_open_icon",
    "folder_yellow_open_icon",
    "folder_blue_light_open_icon",
]

chooseableItemImages[""] = _("No icon")
