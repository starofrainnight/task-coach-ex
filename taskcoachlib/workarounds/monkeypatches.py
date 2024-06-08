# -*- coding: utf-8 -*-

import wx
import inspect
from collections import namedtuple
from wx.core import Window

try:
    inspect.getargspec
except AttributeError:
    ArgSpec = namedtuple("ArgSpec", "args varargs keywords defaults")

    # Workaround for getargspec() missing inspect.getargspec() for python3.11 or later
    def getargspec(func):
        """Get the names and default values of a function's parameters.

        A tuple of four things is returned: (args, varargs, keywords, defaults).
        'args' is a list of the argument names, including keyword-only argument names.
        'varargs' and 'keywords' are the names of the * and ** parameters or None.
        'defaults' is an n-tuple of the default values of the last n parameters.

        This function is deprecated, as it does not support annotations or
        keyword-only parameters and will raise ValueError if either is present
        on the supplied callable.

        For a more structured introspection API, use inspect.signature() instead.

        Alternatively, use getfullargspec() for an API with a similar namedtuple
        based interface, but full support for annotations and keyword-only
        parameters.

        Deprecated since Python 3.5, use `inspect.getfullargspec()`.
        """
        from inspect import getfullargspec

        args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = (
            getfullargspec(func)
        )
        if kwonlyargs or ann:
            raise ValueError(
                "Function has keyword-only parameters or annotations"
                ", use inspect.signature() API which can support them"
            )
        return ArgSpec(args, varargs, varkw, defaults)

    inspect.getargspec = getargspec

Window_SetSizeOld = Window.SetSize


def Window_SetSizeNew(self, *args, **kw):
    """
    SetSize(x, y, width, height, sizeFlags=SIZE_AUTO)
    SetSize(rect)
    SetSize(size)
    SetSize(width, height)

    Sets the size of the window in pixels.

    This monkey patch fixed the Gtk-CRITICAL **: 21:21:53.043:
    gtk_widget_set_size_request: assertion 'height >= -1' failed
    """
    if len(args) <= 1:
        arg = args[0]
        if arg is wx.Size:
            width = 0 if arg.Width < 0 else arg.Width
            height = 0 if arg.Height < 0 else arg.Height
            Window_SetSizeOld(self, width, height)
        elif arg is wx.Rect:
            width = 0 if arg.width < 0 else arg.width
            height = 0 if arg.height < 0 else arg.height
            Window_SetSizeOld(self, wx.Rect(arg.x, arg.y, width, height))
        else:
            Window_SetSizeOld(self, *args, **kw)
    elif len(args) <= 2:
        width = args[0]
        height = args[1]
        width = 0 if width < 0 else width
        height = 0 if height < 0 else height
        Window_SetSizeOld(self, width, height)
    else:
        x = args[0]
        y = args[1]
        width = args[2]
        height = args[3]
        width = 0 if width < 0 else width
        height = 0 if height < 0 else height
        Window_SetSizeOld(self, x, y, width, height, *args[4:], **kw)


Window.SetSize = Window_SetSizeNew
