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

        return f"{self.name} -> {self.alias}"

    def __eq__(self, other) -> bool:
        """Compares us to another module

        :param self:
            Self
        :param other:
            The module to compare to

        :return True:
            We are equal to the other module
        :return False;
            We are not equal to the other module
        """

        if other is None:
            return False

        return (self.name == other.name) and (self.alias == other.alias)

    def __ne__(self, other) -> bool:
        """Compares us to another module

        :param self:
            Self
        :param other:
            The module to compare to

        :return True:
            We are not equal to the other module
        :return False:
            We are equal to the other module
        """

        return not (self == other)
