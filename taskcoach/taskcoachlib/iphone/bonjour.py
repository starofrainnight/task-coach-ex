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

from taskcoachlib.thirdparty import pybonjour
from twisted.internet.interfaces import IReadDescriptor
from twisted.internet.defer import Deferred, AlreadyCalledError
from twisted.python.failure import Failure
from zope import interface


class BonjourServiceDescriptor(object):
    interface.implements(IReadDescriptor)

    def __init__(self):
        self.__fd = None

    def start(self, fd):
        from twisted.internet import reactor

        self.__fd = fd
        reactor.addReader(self)

    def stop(self):
        if self.__fd is not None:
            from twisted.internet import reactor

            reactor.removeReader(self)
            self.__fd.close()
            self.__fd = None

    def doRead(self):
        if self.__fd is not None:
            pybonjour.DNSServiceProcessResult(self.__fd)

    def fileno(self):
        return None if self.__fd is None else self.__fd.fileno()

    def logPrefix(self):
        return "bonjour"

    def connectionLost(self, reason):
        if self.__fd is not None:
            self.__fd.close()


def BonjourServiceRegister(settings, port):
    from twisted.internet import reactor

    d = Deferred()
    reader = BonjourServiceDescriptor()

    def registerCallback(sdRef, flags, errorCode, name, regtype, domain):
        try:
            if errorCode == pybonjour.kDNSServiceErr_NoError:
                d.callback(reader)
            else:
                reader.stop()
                d.errback(
                    Failure(
                        RuntimeError(
                            "Could not register with Bonjour: %d" % errorCode
                        )
                    )
                )
        except AlreadyCalledError:
            pass

    # This ID is registered, see http://www.dns-sd.org/ServiceTypes.html
    sdRef = pybonjour.DNSServiceRegister(
        name=settings.get("iphone", "service") or None,
        regtype="_taskcoachsync._tcp",
        port=port,
        callBack=registerCallback,
    )
    reader.start(sdRef)
    return d
