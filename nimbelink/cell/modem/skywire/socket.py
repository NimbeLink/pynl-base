"""
A Skywire socket factory

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import socket
import typing

class Socket(object):
    """A Skywire socket factory
    """

    class Instance:
        """A usable socket object
        """

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
        ) -> "Socket.Instance":
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

            :raise OSError:
                Failed to create new socket on modem
            :raise OSError:
                Failed to find file descriptor

            :return none:
            """

            raise NotImplementedError("create() not implemented by {}".format(self.__class__.__name__))

        def close(self) -> None:
            """Closes the socket

            :param self:
                Self

            :return none:
            """

            raise NotImplementedError("close() not implemented by {}".format(self.__class__.__name__))

        def connect(self, address: typing.Tuple[str, int]) -> None:
            """Connects to an address

            :param self:
                Self
            :param address:
                A tuple of the host string and port number

            :raise OSError:
                Failed to connect socket

            :return none:
            """

            raise NotImplementedError("connect() not implemented by {}".format(self.__class__.__name__))

        def send(self, bytes: bytearray) -> int:
            """Sends data to the socket

            :param self:
                Self
            :param bytes:
                The data to send

            :return Integer:
                The number of bytes sent
            """

            raise NotImplementedError("send() not implemented by {}".format(self.__class__.__name__))

        def recv(self, bufsize: int) -> bytearray:
            """Receives data from the socket

            :param self:
                Self
            :param bufsize:
                The amount of data to receive

            :return bytearray:
                The received data
            """

            raise NotImplementedError("recv() not implemented by {}".format(self.__class__.__name__))

    def __call__(self, *args, **kwargs) -> "Socket.Instance":
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

        raise NotImplementedError("__call__() not implemented by {}".format(self.__class__.__name__))
