"""
A configuration storage backend

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

class Backend:
    """A configuration storage backend
    """

    def getDict(self) -> dict:
        """Gets a dictionary from this backend

        :param self:
            Self

        :return dict:
            Our dictionary
        """

        raise NotImplementedError("I never learned to read")

    def setDict(self, data: dict) -> None:
        """Sets this backend's dictionary

        :param self:
            Self
        :param data:
            The data to set

        :return none:
        """

        raise NotImplementedError("I never learned to write")

    def format(self, data: dict) -> str:
        """Gets a string representation of a dictionary

        :param self:
            Self
        :param data:
            The data to format a string for

        :return str:
            The formatted string
        """

        raise NotImplementedError("I never developed eyes")
