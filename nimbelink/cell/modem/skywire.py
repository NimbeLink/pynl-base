###
 # \file
 #
 # \brief A Skywire modem
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import time

class Skywire(object):
    """A Skywire modem
    """

    class AtError(Exception):
        """An error that occurs when an AT command fails with an error
        """

        def __init__(self, response, message = None):
            """Creates a new AT error

            :param self:
                Self
            :param response:
                The AT command's response
            :param message:
                A message about the failure

            :return none:
            """

            if message == None:
                message = "AT command failed"

            if response != None:
                message += ": {}".format(response)

            self._response = response
            self._message = message

            super(Skywire.AtError, self).__init__(self._message)

    def __init__(self, at):
        """Creates a new Skywire modem

        :param self:
            Self
        :param at:
            Our AT interface

        :return none:
        """

        self._at = at

    @property
    def at(self):
        """Gets our AT interface

        :param self:
            Self

        :return AtInterface:
            Our AT interface
        """

        return self._at

    @property
    def networkMode(self):
        """Gets the current network mode

        :param self:
            Self

        :raise Skywire.AtError:
            Failed to get network mode

        :return Network.Mode:
            The current network mode
        """

        response = self.at.sendCommand("AT+CEREG?")

        # If we failed to query the network mode, that's a paddlin'
        if not response:
            raise Skywire.AtError(response, "Failed to query network mode")

        lines = response.lines

        if len(lines) < 1:
            raise Skywire.AtError(response, "Invalid network mode response")

        fields = lines[0].split(",")

        # If there isn't at least the prefix and the current mode, that's a
        # paddlin'
        if len(fields) < 2:
            raise Skywire.AtError(response, "Invalid network mode response")

        try:
            return int(fields[1])

        except ValueError:
            raise Skywire.AtError(response, "Invalid network mode")

    @networkMode.setter
    def networkMode(self, networkMode):
        """Sets our network mode

        :param self:
            Self
        :param networkMode:
            The network mode to set

        :raise Skywire.AtError:
            Failed to set network mode

        :return none:
        """

        # Setting the network mode can take a bit of time, so give it 10 seconds
        # to finish
        response = self.at.sendCommand("AT+CFUN={}".format(networkMode), timeout = 10)

        if not response:
            raise Skywire.AtError(response, "Failed to set network mode")
