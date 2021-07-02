"""
Interfaces with a host application through a CTRL-AP mailbox

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

from .ctrlAp import CtrlAp

class Mailbox:
    """A host application interface
    """

    class Packet:
        def __init__(self, type: int, length: int, data: typing.List[int] = None) -> None:
            """Creates a new packet

            :param self:
                Self
            :param type:
                The type of the packet
            :param length:
                The length of the packet
            :param data:
                The data payload

            :return none:
            """

            if data is None:
                data = []

            self.type = type
            self.length = length
            self.data = data

            self.buffer = [
                type,
                length
            ] + data

        @staticmethod
        def makeFromBuffer(buffer: typing.List[int]) -> "Mailbox.Packet":
            """Creates a new packet

            :param self:
                Self
            :param buffer:
                The packet buffer

            :return None:
                Buffer doesn't contain a valid packet
            :return Packet:
                The packet
            """

            # If this buffer won't form a real packet, don't try making one
            if len(buffer) < 2:
                return None

            return Mailbox.Packet(
                type = buffer[0],
                length = buffer[1],
                data = buffer[2:]
            )

    class Target:
        Monitor     = 0
        """The Secure primary application"""

        Widget      = 1
        """The Non-Secure secondary application"""

    class Request:
        Ping        = 0
        """Does a simple ping with the device"""

        Dfu         = 1
        """Starts an Device Firmware Update process"""

        Convert     = 2
        """Converts the device to flash-able"""

    class Response:
        Unknown     = 0
        """The request was unknown"""

        Ok          = 1
        """Request successfully handled"""

        Error       = 2
        """Request failed"""

    def __init__(self, ctrlAp: CtrlAp) -> None:
        """Creates a new mailbox interface

        :param self:
            Self
        :param ctrlAp:
            The CTRL-AP to use

        :return none:
        """

        self._ctrlAp = ctrlAp

    def _sendRequest(self, request: "Mailbox.Request", timeout: float = 1.0) -> bool:
        """Sends a request over our mailbox interface

        :param self:
            Self
        :param request:
            The request to send
        :param timeout:
            How long to wait for a response

        :return True:
            Packet sent and acknowledged
        :return False:
            Packet not acknowledged
        :return None:
            No response
        """

        self._ctrlAp.clear()

        # If we fail to send the request, that's a paddlin'
        if not self._ctrlAp.writeMailbox(values = request.buffer, timeout = 3.0):
            return None

        # Try to get the response
        response = self._ctrlAp.readMailbox(length = 2, timeout = timeout)

        # If there wasn't a response, that's a paddlin'
        if not response:
            return None

        response = Mailbox.Packet.makeFromBuffer(buffer = response)

        # If the response was somehow borked, that's a paddlin'
        if not response:
            return False

        # If the response wasn't ACKed, that's a paddlin'
        if response.type != Mailbox.Response.Ok:
            return False

        return True

    def ping(self) -> bool:
        """Pings the device

        :param self:
            Self

        :return True:
            Device pinged
        :return False:
            Failed to ping device
        """

        # Form the request
        request = Mailbox.Packet(
            type = Mailbox.Request.Ping,
            length = 0
        )

        if self._sendRequest(request = request):
            return True

        return False

    def dfu(self, autoReboot: bool = None) -> bool:
        """Starts an application DFU

        :param self:
            Self
        :param autoReboot:
            Whether or not to automatically reboot after a successful DFU
            transfer

        :return True:
            DFU started
        :return False:
            Failed to start DFU
        """

        if autoReboot is None:
            autoReboot = True

        # Form the request
        request = Mailbox.Packet(
            type = Mailbox.Request.Dfu,
            length = 1,
            data = [
                int(autoReboot)
            ]
        )

        if self._sendRequest(request = request):
            return True

        return False

    def convert(self) -> bool:
        """Converts a device

        :param self:
            Self

        :return True:
            Device converted
        :return False:
            Failed to convert device
        """

        # Form the request
        request = Mailbox.Packet(
            type = Mailbox.Request.Convert,
            length = 0
        )

        # If we get anything other than a timeout when starting the conversion,
        # it went awry and that's a paddlin'
        if self._sendRequest(request = request) is not None:
            return False

        # Wait for the device to start responding to our pings, giving it a bit
        # of time to finish the erasing and rebooting processes
        for i in range(10):
            if self.ping():
                return True

        return False
