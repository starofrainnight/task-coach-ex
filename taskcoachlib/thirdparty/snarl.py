# Python Snarl bindings version 0.2a
# Hacked together by Alexander Lash in the wee hours of 2/27.
# Contact him at alexander.lash@gmail.com
# 0.1a: Initial release
# 0.2a: Added basic command line functions
# LARGELY UNTESTED REFERENCE IMPLEMENTATION
import win32gui, win32api, win32con
import struct, array
from ctypes import cast, POINTER, c_byte


class SNARL_COMMANDS:
    SNARL_SHOW = 1
    SNARL_HIDE = 2
    SNARL_UPDATE = 3
    SNARL_IS_VISIBLE = 4
    SNARL_GET_VERSION = 5
    SNARL_REGISTER_CONFIG_WINDOW = 6
    SNARL_REVOKE_CONFIG_WINDOW = 7
    SNARL_REGISTER_ALERT = 8
    SNARL_REVOKE_ALERT = 9
    SNARL_REGISTER_CONFIG_WINDOW_2 = 0xA
    SNARL_EX_SHOW = 0x20

    @staticmethod
    def sendCommand(
        command,
        id=0,
        timeout=0,
        longdata=0,
        title="",
        text="",
        icon="",
        extra=None,
        extra2=None,
        reserved1=None,
        reserved2=None,
    ):
        if (
            extra is None
            and extra2 is None
            and reserved1 is None
            and reserved2 is None
        ):
            command = struct.pack(
                "ILLL1024s1024s1024s",
                command,
                id,
                timeout,
                longdata,  # LngData2
                array.array("B", title).tostring(),
                array.array("B", text).tostring(),
                array.array("B", icon).tostring(),
            )
        else:
            if reserved1 is None:
                reserved1 = 0
            if reserved2 is None:
                reserved2 = 0
            if extra is None:
                extra = ""
            if extra2 is None:
                extra2 = ""
            command = struct.pack(
                "ILLL1024s1024s1024s1024s1024sLL",
                command,
                id,
                timeout,
                longdata,  # LngData2
                array.array("B", title).tostring(),
                array.array("B", text).tostring(),
                array.array("B", icon).tostring(),
                array.array("B", extra).tostring(),
                array.array("B", extra2).tostring(),
                reserved1,
                reserved2,
            )
        command_pack = array.array("B", command)
        command_info = command_pack.buffer_info()

        cd = struct.pack("LLP", 2, command_info[1], command_info[0])
        cd_pack = array.array("B", cd)
        cd_info = cd_pack.buffer_info()

        hwnd = win32gui.FindWindow(None, "Snarl")
        if hwnd:
            return win32api.SendMessage(
                hwnd, win32con.WM_COPYDATA, 0, cd_info[0]
            )
        else:
            return False


# deviation from spec: Python doesn't do references.
def snGetVersion():
    hr = SNARL_COMMANDS.sendCommand(SNARL_COMMANDS.SNARL_GET_VERSION)
    if hr:
        ver = cast(hr, POINTER(c_byte))
        return (ver[0], ver[1])
    return False


# deviation from spec: sound is an optional parameter.
def snShowMessage(
    title, text, timeout=0, iconPath="", reply=0, reply_msg=0, sound=None
):
    if title is None or text is None:
        return False
    if sound is None:
        return SNARL_COMMANDS.sendCommand(
            SNARL_COMMANDS.SNARL_SHOW,
            reply,
            timeout,
            reply_msg,
            title,
            text,
            iconPath,
        )
    return SNARL_COMMANDS.sendCommand(
        SNARL_COMMANDS.SNARL_SHOW,
        reply,
        timeout,
        reply_msg,
        title,
        text,
        iconPath,
        sound,
    )


def snUpdateMessage(id, title, text):
    if id is None or title is None or text is None:
        return False
    return (
        SNARL_COMMANDS.sendCommand(
            SNARL_COMMANDS.SNARL_UPDATE, id=id, title=title, text=text
        )
        == -1
    )


def snHideMessage(id):
    id = int(id)
    if id is None:
        return False
    return SNARL_COMMANDS.sendCommand(SNARL_COMMANDS.SNARL_HIDE, id=id) == -1


# For some reason this ALWAYS returns -1 for all messages that were once displayed.
def snIsMessageVisible(id):
    return (
        SNARL_COMMANDS.sendCommand(SNARL_COMMANDS.SNARL_IS_VISIBLE, id=id)
        == -1
    )


# Untested
def snRegisterConfig(hwnd, appname, reply_msg, icon=None):
    if icon is None:
        return SNARL_COMMANDS.sendCommand(
            SNARL_COMMANDS.SNARL_REGISTER_CONFIG_WINDOW,
            longdata=hwnd,
            title=appname,
            id=reply_msg,
        )
    return SNARL_COMMANDS.sendCommand(
        SNARL_COMMANDS.SNARL_REGISTER_CONFIG_WINDOW,
        longdata=hwnd,
        title=appname,
        id=reply_msg,
        icon=icon,
    )


# Untested
def snRevokeConfig(hwnd):
    return SNARL_COMMANDS.sendCommand(
        SNARL_COMMANDS.SNARL_REVOKE_CONFIG_WINDOW, longdata=hwnd
    )


# Reference implementation - seems to do nothing?
def snRegisterAlert(title, text):
    return SNARL_COMMANDS.sendCommand(
        SNARL_COMMANDS.SNARL_REGISTER_ALERT, title=title, text=text
    )


# Reference implementation - seems to do nothing?
def snRevokeAlert():
    return SNARL_COMMANDS.sendCommand(SNARL_COMMANDS.SNARL_REVOKE_ALERT)


if __name__ == "__main__":
    import sys, inspect
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        "-s",
        "--show",
        action="store_const",
        dest="cmd",
        const=snShowMessage,
        help="Show a message with the given parameters.",
    )
    parser.add_option(
        "-u",
        "--update",
        action="store_const",
        dest="cmd",
        const=snUpdateMessage,
        help="Update a message with the given parameters.",
    )
    parser.add_option(
        "-c",
        "--hide",
        action="store_const",
        dest="cmd",
        const=snHideMessage,
        help="Hide a message with the given ID.",
    )
    parser.add_option(
        "-i", "--id", dest="id", help="ID to use for the update/hide."
    )
    parser.add_option(
        "-t", "--title", dest="title", help="Title to use for the show/update."
    )
    parser.add_option(
        "-x", "--text", dest="text", help="Text to use for the show/update."
    )
    parser.add_option(
        "-T", "--timeout", dest="timeout", help="Timeout to use for the show."
    )
    parser.add_option(
        "-I", "--icon", dest="iconPath", help="Icon to use for the show."
    )
    parser.add_option(
        "-S", "--sound", dest="sound", help="Sound to use for the show."
    )
    if snGetVersion == False:
        print("Snarl not running!")
        sys.exit(1)
    (options, args) = parser.parse_args(sys.argv[1:])
    if options.cmd is None:
        parser.parse_args(["-h"])
    d = options.__dict__.copy()
    cmd = options.cmd
    for key in options.__dict__:
        if key not in inspect.getargspec(cmd)[0]:
            del d[key]
        elif d[key] is None:
            del d[key]
    print(cmd(**d))
    sys.exit(0)
