"""
An installable NimbeLink Python package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

class Module:
    """An installable NimbeLink Python package
    """

    def __init__(self, name: str, alias: str) -> None:
        """Creates a new module

        :param self:
            Self
        :param name:
            The name of the installable module
        :param alias:
            The local alias to use when linking it into the 'nimbelink' package

        :return none:
        """

        self.name = name
        self.alias = alias

    def __str__(self) -> str:
        """Gets a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        return "{} -> {}".format(self.name, self.alias)
