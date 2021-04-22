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

    def __init__(self, atInterface):
        """Creates a new Skywire modem

        :param self:
            Self
        :param atInterface:
            Our AT interface

        :return none:
        """

        self.atInterface = atInterface

    def setNetworkMode(self, networkMode):
        """Sets our network mode

        :param self:
            Self
        :param networkMode:
            The network mode to set

        :return True:
            Network mode set
        :return False:
            Failed to set network mode
        """

        # Setting the network mode can take a bit of time, so give it 10 seconds
        # to finish
        if not self.atInterface.sendCommand("AT+CFUN={}".format(networkMode), timeout = 10):
            return False

        return True

    def getNetworkMode(self):
        """Gets the current network mode

        :param self;
            Self

        :return None:
            Failed to get network mode
        :return Network.Mode:
            The current network mode
        """

        response = self.atInterface.sendCommand("AT+CEREG?")

        # If we failed to query the network mode, that's a paddlin'
        if not response:
            return None

        fields = response.output.split(",")

        # If there isn't at least the prefix and the current mode, that's a
        # paddlin'
        if len(fields) < 2:
            return None

        try:
            return int(fields[1])

        except ValueError:
            return None

    def waitForNetworkMode(self, networkMode, timeout = None):
        """Waits for the modem to reach a network mode

        :param self:
            Self
        :param networkMode:
            The network mode to wait for
        :param timeout:
            How long to wait

        :return True:
            Network mode reached
        :return False:
            Failed to read network mode before timeout
        """

        start = time.time()

        while True:
            # If it's been too long, that's a paddlin'
            if (timeout != None) and ((time.time() - start) >= timeout):
                return False

            # If the modem is at the desired network mode, done
            if self.getNetworkMode() == networkMode:
                return True

            time.sleep(2)
