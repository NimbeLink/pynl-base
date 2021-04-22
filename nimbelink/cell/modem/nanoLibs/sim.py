###
 # \file
 #
 # \brief Skywire Nano SIM resources
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

class Sim:
    """Skywire Nano SIM resources
    """

    Count = 2
    """The Skywire Nano supports up to 2 SIMs"""

    def __init__(self, nano):
        """Creates a new GPIO sub-module

        :param self:
            Self
        :param nano:
            The Skywire Nano we're attached to

        :return none:
        """

        self._nano = nano

    @property
    def index(self, index):
        """Sets our active SIM

        :param self:
            Self
        :param index:
            Which SIM to select

        :raise IOError:
            Failed to select SIM

        :return none:
        """

        if not self._nano.at.sendCommand("AT#SIMSELECT={}".format(index)):
            raise IOError("Failed to set SIM index")

        return True

    @property
    def iccid(self):
        """Gets our SIM's ICCID

        :param self:
            Self

        :raise IOError:
            Failed to get ICCID

        :return String:
            The ICCID
        """

        response = self._nano.at.sendCommand("AT#ICCID?")

        if not response or (len(response.output) < 1):
            raise IOError("Failed to query ICCID")

        return response.output
