###
 # \file
 #
 # \brief A Skywire Nano modem
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

from nimbelink.cell.modem.skywire import Skywire

from nimbelink.cell.modem.nano.gpio import Gpio
from nimbelink.cell.modem.nano.sim import Sim
from nimbelink.cell.modem.nano.socket import Socket

class SkywireNano(Skywire):
    """A Skywire modem
    """

    def __init__(self, *args, **kwargs):
        """Creates a new Skywire Nano modem

        :param self:
            Self
        :param *args:
            Positional arguments
        :param **kwargs:
            Keyword arguments

        :return none:
        """

        super(SkywireNano, self).__init__(*args, **kwargs)

        self._gpio = Gpio(self)
        self._sim = Sim(self)
        self._socket = Socket(self)

    @property
    def gpio(self):
        """Gets our GPIOs

        :param self:
            Self

        :return Gpio:
            Our GPIOs
        """

        return self._gpio

    @property
    def sim(self):
        """Gets our SIM

        :param self:
            Self

        :return Sim:
            Our SIM
        """

        return self._sim

    @property
    def socket(self):
        """Gets our socket

        :param self:
            Self

        :return Socket:
            Our socket
        """

        return self._socket

    @property
    def versions(self):
        """Gets our versions

        :param self:
            Self

        :raise IOError:
            Failed to get versions

        :return Array of tuples:
            The version names and their values
        """

        # Get the stack and AT interface versions
        response = self.at.sendCommand("AT#APPVER?")

        # If that failed, that's a paddlin'
        if not response:
            raise IOError("Failed to get app versions")

        # Get the version lines
        versions = response.output.split(self.at.NewLine)

        # If there aren't two versions, that's a paddlin'
        if len(versions) != 2:
            raise IOError("Failed to get all app versions")

        for i in range(len(versions)):
            # Each version follows '#APPVER: <thing>: <version>'
            fields = versions[i].split(":")

            # If that wasn't the case for any version, that's a paddlin'
            if len(fields) != 3:
                raise IOError("Invalid app version response")

            # Make sure we remove any whitespace
            versions[i] = (fields[1].strip(), fields[2].strip())

        # Get the modem/co-processor version
        response = self.at.sendCommand("AT+CGMR")

        # If that failed, that's a paddlin'
        if not response:
            raise IOError("Failed to get co-processor version")

        # If there isn't a single version, that's a paddlin'
        if len(response.output) < 1:
            raise IOError("Invalid co-processor version response")

        # The modem version is just a single string, so add our own identifier
        # for it
        versions.append(("MFW", response.output))

        return versions
