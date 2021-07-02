"""
A Skywire modem

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import logging
import time

import nimbelink.cell.at as at
import nimbelink.cell.modem as modem

from nimbelink.cell.modem.skywire.app import App
from nimbelink.cell.modem.skywire.gpio import Gpio
from nimbelink.cell.modem.skywire.host import Host
from nimbelink.cell.modem.skywire.sim import Sim
from nimbelink.cell.modem.skywire.socket import Socket

class Skywire(object):
    """A Skywire modem
    """

    def __init__(
        self,
        app: App,
        interface: at.Interface,
        gpio: Gpio,
        sim: Sim,
        socket: Socket
    ) -> None:
        """Creates a new Skywire modem

        :param self:
            Self
        :param app:
            An app sub-module
        :param interface:
            Our AT interface
        :param gpio:
            A GPIO sub-module
        :param sim:
            A SIM sub-module
        :param socket:
            A socket sub-module

        :return none:
        """

        self._app = app
        self._interface = interface
        self._gpio = gpio
        self._sim = sim
        self._socket = socket

        self._host = None

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def app(self) -> App:
        """Gets our app sub-module

        :param self:
            Self

        :return App:
            Our app sub-module
        """

        return self._app

    @property
    def at(self) -> at.Interface:
        """Gets our AT interface

        :param self:
            Self

        :return Interface:
            Our AT interface
        """

        return self._interface

    @property
    def gpio(self) -> Gpio:
        """Gets our GPIO sub-module

        :param self:
            Self

        :return Gpio:
            Our GPIO sub-module
        """

        return self._gpio

    @property
    def sim(self) -> Sim:
        """Gets our SIM sub-module

        :param self:
            Self

        :return Sim:
            Our SIM sub-module
        """

        return self._sim

    @property
    def socket(self) -> Socket:
        """Gets our socket sub-module

        :param self:
            Self

        :return Socket:
            Our socket sub-module
        """

        return self._socket

    @property
    def host(self) -> Host:
        """Gets our host

        :param self:
            Self

        :return Host:
            Our host
        """

        raise NotImplementedError(f"host() not implemented by {self.__class__.__name__}")

    @host.setter
    def host(self, newHost: Host):
        """Sets our host

        :param self:
            Self
        :param newHost:
            The host to use

        :return none:
        """

        self._host = newHost

    @property
    def networkMode(self):
        """Gets the current network mode

        :param self:
            Self

        :raise AtError:
            Failed to get network mode

        :return Mode:
            The current network mode
        """

        response = self.at.sendCommand("AT+CEREG?")

        # If we failed to query the network mode, that's a paddlin'
        if not response:
            raise modem.AtError(response, "Failed to query network mode")

        lines = response.lines

        if len(lines) < 1:
            raise modem.AtError(response, "Invalid network mode response")

        fields = lines[0].split(",")

        # If there isn't at least the prefix and the current mode, that's a
        # paddlin'
        if len(fields) < 2:
            raise modem.AtError(response, "Invalid network mode response")

        try:
            return int(fields[1])

        except ValueError:
            raise modem.AtError(response, "Invalid network mode")

    @networkMode.setter
    def networkMode(self, networkMode):
        """Sets our network mode

        :param self:
            Self
        :param networkMode:
            The network mode to set

        :raise AtError:
            Failed to set network mode

        :return none:
        """

        # Setting the network mode can take a bit of time, so give it 10 seconds
        # to finish
        response = self.at.sendCommand(f"AT+CFUN={networkMode}", timeout = 10)

        if not response:
            raise modem.AtError(response, "Failed to set network mode")

    def reboot(self) -> None:
        """Gracefully reboot the modem

        :param self:
            Self

        :return: None
        :rtype: None
        """

        raise NotImplementedError(f"reboot() not implemented by {self.__class__.__name__}")

    def shutdown(self) -> None:
        """Gracefully shut down the modem

        :param self:
            Self

        :return: None
        :rtype: None
        """

        raise NotImplementedError(f"shutdown() not implemented by {self.__class__.__name__}")

    def reset(self) -> None:
        """Hard reset the modem

        WARNING: It is recommended to detach from the network before hard
        resetting the modem.

        :param self:
            Self

        :return: None
        :rtype: None
        """

        self.host.reset()
