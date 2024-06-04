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

import os, select, time, threading

from ctypes import *

_libSM = CDLL("libSM.so.6")
_libICE = CDLL("libICE.so.6")

# ==============================================================================
# ICE stuff...

Bool = c_int
Status = c_int


class _IceConn(Structure):
    pass


IceConn = POINTER(_IceConn)

IceWatchProc = CFUNCTYPE(None, IceConn, c_void_p, Bool, POINTER(c_void_p))

IceInitThreads = CFUNCTYPE(Status)(("IceInitThreads", _libICE))
IceAddConnectionWatch = CFUNCTYPE(Status, IceWatchProc, c_void_p)(
    ("IceAddConnectionWatch", _libICE)
)
IceRemoveConnectionWatch = CFUNCTYPE(None, IceWatchProc, c_void_p)(
    ("IceRemoveConnectionWatch", _libICE)
)
IceConnectionNumber = CFUNCTYPE(c_int, IceConn)(
    ("IceConnectionNumber", _libICE)
)
IceProcessMessages = CFUNCTYPE(c_int, IceConn, c_void_p, c_void_p)(
    ("IceProcessMessages", _libICE)
)
IceCloseConnection = CFUNCTYPE(c_int, IceConn)(("IceCloseConnection", _libICE))

IceIOErrorHandler = CFUNCTYPE(None, IceConn)

IceSetIOErrorHandler = CFUNCTYPE(IceIOErrorHandler, IceIOErrorHandler)(
    ("IceSetIOErrorHandler", _libICE)
)

# ==============================================================================
# Constants

# Callback masks

SmcSaveYourselfProcMask = 1 << 0
SmcDieProcMask = 1 << 1
SmcSaveCompleteProcMask = 1 << 2
SmcShutdownCancelledProcMask = 1 << 3

# Status

SmcClosedNow = 0
SmcClosedASAP = 1
SmcConnectionInUse = 2

# Interaction types

SmInteractStyleNone = 0
SmInteractStyleErrors = 1
SmInteractStyleAny = 2

# Save types

SmSaveGlobal = 0
SmSaveLocal = 1
SmSaveBoth = 2

# Restart hints

SmRestartIfRunning = 0
SmRestartAnyway = 1
SmRestartImmediately = 2
SmRestartNever = 3

# Property types

SmCARD8 = "CARD8"  # Single character
SmARRAY8 = "ARRAY8"  # String
SmLISTofARRAY8 = "LISTofARRAY8"  # List of strings

# Property names

SmCloneCommand = "CloneCommand"
SmCurrentDirectory = "CurrentDirectory"
SmDiscardCommand = "DiscardCommand"
SmEnvironment = "Environment"
SmProcessID = "ProcessID"
SmProgram = "Program"
SmRestartCommand = "RestartCommand"
SmResignCommand = "ResignCommand"
SmRestartStyleHint = "RestartStyleHint"
SmShutdownCommand = "ShutdownCommand"
SmUserID = "UserID"

# ==============================================================================
# Types and structures


class _SmcConn(Structure):
    pass


SmcConn = POINTER(_SmcConn)

SmcSaveYourselfProc = CFUNCTYPE(
    None, SmcConn, c_void_p, c_int, Bool, c_int, Bool
)
SmcDieProc = CFUNCTYPE(None, SmcConn, c_void_p)
SmcSaveCompleteProc = CFUNCTYPE(None, SmcConn, c_void_p)
SmcShutdownCancelledProc = CFUNCTYPE(None, SmcConn, c_void_p)


class SmcSaveYourselfCallback(Structure):
    _fields_ = [("callback", SmcSaveYourselfProc), ("client_data", c_void_p)]


class SmcDieCallback(Structure):
    _fields_ = [("callback", SmcDieProc), ("client_data", c_void_p)]


class SmcSaveCompleteCallback(Structure):
    _fields_ = [("callback", SmcSaveCompleteProc), ("client_data", c_void_p)]


class SmcShutdownCancelledCallback(Structure):
    _fields_ = [
        ("callback", SmcShutdownCancelledProc),
        ("client_data", c_void_p),
    ]


class SmcCallbacks(Structure):
    _fields_ = [
        ("save_yourself", SmcSaveYourselfCallback),
        ("die", SmcDieCallback),
        ("save_complete", SmcSaveCompleteCallback),
        ("shutdown_cancelled", SmcShutdownCancelledCallback),
    ]


class SmPropValue(Structure):
    _fields_ = [("length", c_int), ("value", c_void_p)]


class SmProp(Structure):
    _fields_ = [
        ("name", c_char_p),
        ("type", c_char_p),
        ("num_vals", c_int),
        ("values", POINTER(SmPropValue)),
    ]


# ==============================================================================
# Functions

SmcOpenConnection = CFUNCTYPE(
    SmcConn,
    c_char_p,
    c_void_p,
    c_int,
    c_int,
    c_ulong,
    POINTER(SmcCallbacks),
    c_char_p,
    POINTER(c_char_p),
    c_int,
    c_char_p,
)(("SmcOpenConnection", _libSM))

SmcCloseConnection = CFUNCTYPE(c_int, SmcConn, c_int, POINTER(c_char_p))(
    ("SmcCloseConnection", _libSM)
)

SmcModifyCallbacks = CFUNCTYPE(None, SmcConn, c_ulong, POINTER(SmcCallbacks))(
    ("SmcModifyCallbacks", _libSM)
)

SmcSaveYourselfDone = CFUNCTYPE(None, SmcConn, Bool)(
    ("SmcSaveYourselfDone", _libSM)
)

SmcProtocolVersion = CFUNCTYPE(c_int, SmcConn)(("SmcProtocolVersion", _libSM))

SmcProtocolRevision = CFUNCTYPE(c_int, SmcConn)(
    ("SmcProtocolRevision", _libSM)
)

SmcVendor = CFUNCTYPE(c_char_p, SmcConn)(("SmcVendor", _libSM))

SmcRelease = CFUNCTYPE(c_char_p, SmcConn)(("SmcRelease", _libSM))

SmcSetProperties = CFUNCTYPE(None, SmcConn, c_int, POINTER(POINTER(SmProp)))(
    ("SmcSetProperties", _libSM)
)

# ==============================================================================
# Higher-level stuff


class ICELoop(threading.Thread):
    """
    This class manages ICE connections tracking and select()ing them
    before calling IceProcessMessages.
    """

    def __init__(self):
        # Don't track all connections. It seems to cause SIGSEGV when ProcessMessages
        # is called on another one
        self.connection = None
        self.cancelled = False

        self.watchProc = IceWatchProc(self._onWatch)

        IceAddConnectionWatch(self.watchProc, None)

        super(ICELoop, self).__init__()

        self.start()

    def stop(self):
        """
        Stop the main loop. Don't forget to join() this afterwards.
        """

        IceRemoveConnectionWatch(self.watchProc, None)
        self.cancelled = True

    def _onWatch(self, conn, client_data, opening, watchdata):
        if opening and self.connection is None:
            self.connection = (conn, IceConnectionNumber(conn))

    def run(self):
        class DummyDescriptor(object):
            def __init__(self, fd):
                self.fd = fd

            def fileno(self):
                return self.fd

        while not self.cancelled:
            if self.connection is not None:
                fds = [DummyDescriptor(self.connection[1])]

                ready, _, _ = select.select(fds, [], [], 1.0)
                if ready:
                    IceProcessMessages(self.connection[0], None, None)
            else:
                time.sleep(1.0)


class SessionMonitor(ICELoop):
    """
    Higher-level class to monitor session management event. Subclass
    this and overload the saveYourself, die, saveComplete and
    shutdownCancelled methods to do actual work.
    """

    def __init__(self):
        super(SessionMonitor, self).__init__()

        self.callbacks = SmcCallbacks(
            SmcSaveYourselfCallback(
                SmcSaveYourselfProc(self._saveYourself), None
            ),
            SmcDieCallback(SmcDieProc(self._die), None),
            SmcSaveCompleteCallback(
                SmcSaveCompleteProc(self._saveComplete), None
            ),
            SmcShutdownCancelledCallback(
                SmcShutdownCancelledProc(self._shutdownCancelled), None
            ),
        )

        id_ret = c_char_p()

        try:
            # Some distros seem to not define this env variable. Strange.
            os.environ["SESSION_MANAGER"]
        except KeyError:
            self.conn = None
        else:
            self.conn = SmcOpenConnection(
                os.environ["SESSION_MANAGER"],
                None,
                1,
                0,
                SmcSaveYourselfProcMask
                | SmcDieProcMask
                | SmcSaveCompleteProcMask
                | SmcShutdownCancelledProcMask,
                byref(self.callbacks),
                None,
                byref(id_ret),
                0,
                None,
            )

            self.clientID = id_ret.value

            IceSetIOErrorHandler(IceIOErrorHandler(self._onIceError))

    def isValid(self):
        return self.conn is not None and self.connection is not None

    def _onIceError(self, conn):
        if self.isValid():
            IceCloseConnection(conn)

        # XXXTODO: retry ? How ?

    def stop(self):
        super(SessionMonitor, self).stop()
        self.join()
        if self.isValid():
            SmcCloseConnection(self.conn, 0, None)

    def setProperty(self, name, value):
        if self.isValid():
            if isinstance(value, str):
                value = value.encode("UTF-8")

            if isinstance(value, str):
                propval = SmPropValue(
                    len(value), cast(c_char_p(value), c_void_p)
                )
                prop = SmProp(name, c_char_p(SmARRAY8), 1, pointer(propval))
                SmcSetProperties(self.conn, 1, pointer(pointer(prop)))
            elif isinstance(value, int):
                value = chr(value)
                propval = SmPropValue(1, cast(c_char_p(value), c_void_p))
                prop = SmProp(name, c_char_p(SmCARD8), 1, pointer(propval))
                SmcSetProperties(self.conn, 1, pointer(pointer(prop)))
            elif isinstance(value, list):
                values = (SmPropValue * len(value))()
                for idx, val in enumerate(value):
                    if isinstance(val, str):
                        val = val.encode("UTF-8")
                    values[idx].length = len(val)
                    values[idx].value = cast(c_char_p(val), c_void_p)
                prop = SmProp(
                    name, c_char_p(SmLISTofARRAY8), len(value), values
                )
                SmcSetProperties(self.conn, 1, pointer(pointer(prop)))
            else:
                raise TypeError(
                    "Unsupported property type: %s" % str(type(value))
                )

    def saveYourselfDone(self, status=True):
        """
        Call this after a save yourself.
        """
        if self.isValid():
            SmcSaveYourselfDone(self.conn, int(status))

    def _saveYourself(
        self, conn, client_data, save_type, shutdown, interact_style, fast
    ):
        if self.isValid():
            self.saveYourself(save_type, shutdown, interact_style, fast)

    def saveYourself(self, save_type, shutdown, interact_style, fast):
        """
        Save yourself request.

        @param save_type: Type of save; see the SmSave* constants.
        @param shutdown: True if a shutdown is in progress.
        @param interact_style: Types of user interactions allowed. See the
            smInteractStyle* constants.
        @param fast: Dunno.
        """
        raise NotImplementedError

    def _die(self, conn, client_data):
        self.die()

    def die(self):
        """
        Die request. A competent session manager should have sent a save
        yourself request before this.
        """
        raise NotImplementedError

    def _saveComplete(self, conn, client_data):
        self.saveComplete()

    def saveComplete(self):
        """
        A save has completed.
        """
        raise NotImplementedError

    def _shutdownCancelled(self, conn, client_data):
        self.shutdownCancelled()

    def shutdownCancelled(self):
        """
        Shutdown cancelled by the user.
        """
        raise NotImplementedError

    # Properties

    @property
    def version(self):
        return SmcProtocolVersion(self.conn) if self.isValid() else None

    @property
    def revision(self):
        return SmcProtocolRevision(self.conn) if self.isValid() else None

    @property
    def vendor(self):
        return SmcVendor(self.conn) if self.isValid() else None  # Leak

    @property
    def release(self):
        return SmcRelease(self.conn) if self.isValid() else None  # Leak


# ==============================================================================
# Testing

if __name__ == "__main__":

    class TestMonitor(SessionMonitor):
        def __init__(self):
            super(TestMonitor, self).__init__()

            print("Version:", self.version)
            print("Revision:", self.revision)
            print("Vendor:", self.vendor)
            print("Release:", self.release)

            print("Client ID:", self.clientID)

        def log(self, msg):
            open("session.txt", "a+").write("==== %s\n" % msg)
            print(msg)

        def saveYourself(self, save_type, shutdown, interact_style, fast):
            self.log(
                "Save yourself %d %d %d %d"
                % (save_type, shutdown, interact_style, fast)
            )
            self.saveYourselfDone(True)

        def die(self):
            self.log("Die")

        def saveComplete(self):
            self.log("Save complete")

        def shutdownCancelled(self):
            self.log("Shutdown cancelled")

    monitor = TestMonitor()
    input("")
    monitor.stop()
    monitor.join()
