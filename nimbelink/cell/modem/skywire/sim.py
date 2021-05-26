"""
Skywire modem SIM utilities

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

class Sim:
    """Skywire modem SIM utilities
    """

    def __init__(self, count: int) -> None:
        """Creates a new SIM sub-module

        :param self:
            Self
        :param count:
            How many SIMs are available

        :return none:
        """

        self._count = count
    def __len__(self) -> int:
        """Gets the number of SIMs available

        :param self:
            Self

        :return int:
            The number of SIMs available
        """

        return self._count

    def setActive(self, index: int) -> None:
        """Sets the currently-selected SIM

        :param self:
            Self
        :param index:
            Which SIM to select

        :return none:
        """

        raise NotImplementedError("setActive() not implemented by {}".format(self.__class__.__name__))

    @property
    def iccid(self) -> str:
        """Gets the current SIM's ICCID

        :param self:
            Self

        :return str:
            The current SIM's ICCID
        """

        raise NotImplementedError("@iccid not implemented by {}".format(self.__class__.__name__))
