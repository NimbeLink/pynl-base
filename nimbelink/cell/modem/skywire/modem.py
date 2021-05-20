"""
A Skywire modem

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import time

import nimbelink.cell.modem as modem

class Skywire(object):
    """A Skywire modem
    """

    def __init__(self, interface):
        """Creates a new Skywire modem

        :param self:
            Self
        :param interface:
            Our AT interface

        :return none:
        """

        self._interface = interface

    @property
    def at(self):
        """Gets our AT interface

        :param self:
            Self

        :return Interface:
            Our AT interface
        """

        return self._interface

    @property
    def host(self):
        """Gets our host

        :param self:
            Self
        :return:
        :rtype: host.Host
        """

        raise NotImplementedError("{c} doesn't implement {c}.host !"
                                            .format(c=self.__class__.__name__))

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
        response = self.at.sendCommand("AT+CFUN={}".format(networkMode), timeout = 10)

        if not response:
            raise modem.AtError(response, "Failed to set network mode")

    def reboot(self) -> None:
        """Gracefully reboot the modem

        :param self:
            Self

        :return: None
        :rtype: None
        """

        raise NotImplementedError("{} doesn't implement reboot()!"
                                            .format(self.__class__.__name__))

    def shutdown(self) -> None:
        """Gracefully shut down the modem

        :param self:
            Self

        :return: None
        :rtype: None
        """

        raise NotImplementedError("{} doesn't implement shutdown()!"
                                            .format(self.__class__.__name__))

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
