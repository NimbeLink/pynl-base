"""
A Skywire Nano socket

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import socket

import nimbelink.cell.modem as modem

class Socket(object):
    """A Skywire Nano socket
    """

    def __init__(self, nano):
        """Creates a new GPIO sub-module

        :param self:
            Self
        :param nano:
            The Skywire Nano we're attached to

        :return none:
        """

        self.nano = nano

    def __call__(self, *args, **kwargs):
        """Creates a new socket

        :param self:
            Self
        :param *args:
            Positional arguments
        :param **kwargs:
            Keyword arguments

        :raise OSError:
            Failed to create new socket

        :return None:
            Failed to create socket
        :return Socket:
            The socket
        """

        instance = Socket.Instance(nano = self.nano)

        instance.create(*args, **kwargs)

        return instance

    class Instance:
        def __init__(self, nano):
            """Creates a new socket instance

            :param self:
                Self
            :param nano:
                The Skywire Nano we're attached to

            :return none:
            """

            self.nano = nano
            self.socketId = None
            self.type = None

            self.recvTimeout = 60

        def __del__(self):
            """Destructs the socket instance

            :param self:
                Self

            :return none:
            """

            self.close()

        def create(
            self,
            family = socket.AF_INET,
            type = socket.SOCK_STREAM,
            proto = 0,
            fileno = None
        ):
            """Creates a new socket

            :param self:
                Self
            :param family:
                The socket family
            :param type:
                The socket type
            :param proto:
                The socket protocol
            :param *args:
                Additional positional arguments
            :param **kwargs:
                Additional keyword arguments

            :raise AtError:
                AT command failed
            :raise OSError:
                Failed to create new socket on modem
            :raise OSError:
                Failed to find file descriptor

            :return none:
            """

            # Get the list of existing sockets
            response = self.nano.at.sendCommand("AT#XSOCKET?")

            # If that failed, that's a paddlin'
            if not response:
                raise modem.AtError(response)

            existingSocketIds = []

            # Make a list of the existing sockets
            for existingSocket in response.lines:
                fields = existingSocket.split(":")

                if len(fields) < 2:
                    continue

                fields = fields[1].strip().split(",")

                if len(fields) < 3:
                    continue

                try:
                    existingSocketIds.append(int(fields[0]))

                except ValueError:
                    pass

            # If they provided a file descriptor to use
            if fileno != None:
                # If the socket ID doesn't exist, that's a paddlin'
                if fileno not in existingSocketIds:
                    raise OSError("fileno {} doesn't exist".format(fileno))

                # Found it, so let's be it too
                self.socketId = fileno

                return

            # Find a socket ID to use
            socketId = 1

            while True:
                if socketId not in existingSocketIds:
                    break

                socketId += 1

            # Try to make the socket
            response = self.nano.at.sendCommand(
                "AT#XSOCKET={},1,{}".format(socketId, type),
                timeout = 30
            )

            # If that failed, that's a paddlin'
            if not response:
                raise OSError("Failed to create new socket on modem")

            lines = response.lines

            # If we didn't get our socket ID response, that's a paddlin'
            if len(lines) < 1:
                raise modem.AtError(response, "Invalid response")

            fields = lines[0].split(":")

            if len(fields) != 2:
                raise modem.AtError(response, "Invalid response")

            fields = fields[1].strip().split(",")

            if len(fields) != 2:
                raise modem.AtError(response, "Invalid response")

            try:
                newSocketId = int(fields[0])

            except TypeError:
                raise modem.AtError(response, "Invalid response")

            # Note our socket ID and socket type
            self.socketId = newSocketId
            self.type = type

        def close(self):
            """Closes the socket

            :param self:
                Self

            :return none:
            """

            if self.socketId != None:
                self.nano.at.sendCommand("AT#XSOCKET={},0".format(self.socketId))

                self.socketId = None

        def connect(self, address):
            """Connects to an address

            :param self:
                Self
            :param address:
                A tuple of the host string and port number

            :raise AtError:
                Failed to send AT command to open socket
            :raise OSError:
                Failed to connect socket

            :return none:
            """

            response = self.nano.at.sendCommand(
                "AT#XTCPCONN={},\"{}\",{}".format(
                    self.socketId,
                    address[0],
                    address[1]
                ),
                timeout = 30
            )

            # If that failed, that's a paddlin'
            if not response:
                raise OSError("Failed to connect socket")

            lines = response.lines

            # If there isn't response output, that's a paddlin'
            if len(lines) < 1:
                raise modem.AtError(response, "Invalid response")

            fields = lines[0].split(":")

            if len(fields) != 2:
                raise modem.AtError(response, "Invalid response")

            try:
                connected = bool(int(fields[1].strip()))

            except ValueError:
                raise modem.AtError(response, "Invalid response")

            # If we didn't connect, that's a paddlin'
            if not connected:
                raise OSError("Failed to connect socket")

        def send(self, bytes):
            """Sends data to the socket

            :param self:
                Self
            :param bytes:
                The data to send

            :return Integer:
                The number of bytes sent
            """

            # We'll want to support sending binary data, so we'll use the
            # prompt-based sender with a static length
            with self.nano.at.startPrompt(dynamic = False) as prompt:
                # Start the prompt
                prompt.startCommand("AT#XTCPSEND={},{}\r".format(
                    self.socketId,
                    len(bytes)
                ))

                # Write the data
                prompt.writeData(data = bytes)

                # Finish our prompt
                response = prompt.finish()

            # If we failed to get a response, that's a paddlin'
            if not response:
                return 0

            # The data might have been echoed, so just use the last line
            fields = response.lines[-1].split(":")

            if len(fields) != 2:
                return 0

            try:
                return int(fields[1].strip())

            except ValueError:
                return 0

        def recv(self, bufsize):
            """Receives data from the socket

            :param self:
                Self
            :param bufsize:
                The amount of data to receive

            :return bytearray:
                The received data
            """

            response = self.nano.at.sendCommand(
                "AT#XTCPRECV={},{},{}".format(
                    self.socketId,
                    bufsize,
                    self.recvTimeout
                ),
                timeout = self.recvTimeout + 5
            )

            # If we failed to get a response, that's a paddlin'
            if not response:
                return bytearray()

            # If there isn't response output, that's a paddlin'
            fields = response.output.split(":", maxsplit = 1)

            if len(fields) != 2:
                return bytearray()

            fields = fields[1].split(",", maxsplit = 1)

            if len(fields) != 2:
                return bytearray()

            # Get the amount of data read
            try:
                size = int(fields[0])

            except ValueError:
                return bytearray()

            # If that doesn't match what we read, that's a paddlin'
            if size != len(fields[1]):
                return bytearray()

            # Return the data
            return fields[1].encode()
