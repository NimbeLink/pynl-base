"""
A base numerical version

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

class Base:
    """A base numerical version
    """

    @staticmethod
    def makeFromString(string: str) -> "Base":
        """Creates a new repository version from a string

        :param string:
            The string to parse

        :return Base:
            The base version
        """

        # If this doesn't start with 'v', we can't be sure it's a version, so
        # just assume it's a name
        if (len(string) < 1) or (string[0] != 'v'):
            return Base(name = string)

        # Drop the 'v', and split this into its components
        fields = string[1:].split(".")

        # If we don't have a major, minor, and tick, that's a paddlin'
        if len(fields) != 3:
            return None

        # Our major and minor are always on their own
        try:
            major = int(fields[0])
            minor = int(fields[1])
            tick = int(fields[2])
        except ValueError:
            return None

        return Base(
            major = major,
            minor = minor,
            tick = tick
        )

    def __init__(
        self,
        major: int = None,
        minor: int = None,
        tick: int = None,
        name: str = None
    ) -> None:
        """Creates a new version base

        :param self:
            Self
        :param major:
            The major field
        :param minor:
            The minor field
        :param tick:
            The tick field
        :param name:
            A simple string name
        :param flavor:
            Flavor

        :return none:
        """

        # If we have any integer values, make sure they didn't give us a name as
        # well
        if ((major is not None) or (minor is not None) or (tick is not None)):
            if name is not None:
                raise ValueError("Cannot mix integers and strings in versions")

        # Else, make sure we have *something* to use
        elif name is None:
            raise ValueError("Cannot have no integers nor strings in versions")

        self.major = major
        self.minor = minor
        self.tick = tick

        self.name = name

    def isName(self) -> bool:
        """Gets if we're a name or an integer version

        :param self:
            Self

        :return True:
            We are a name
        :return False:
            We are not a name
        """

        if ((self.major is None) or
            (self.minor is None) or
            (self.tick is None)
        ):
            return True

        return False

    def increment(
        self,
        major: bool = False,
        minor: bool = False,
        tick: bool = False
    ) -> None:
        """Increments a version

        :param self:
            Self
        :param major:
            Increment the major
        :param minor:
            Increment the minor
        :param tick:
            Increment the tick

        :return none:
        """

        if self.isName():
            raise TypeError("Cannot increment named version")

        if major:
            self.major += 1
            self.minor = 0
            self.tick = 0

        elif minor:
            self.minor += 1
            self.tick = 0

        elif tick:
            self.tick += 1

        else:
            raise ValueError("Must be given something to increment in version")

    def __eq__(self, other: "Base") -> bool:
        """Compares us to another base version

        :param self:
            Self
        :parma other:
            The base version to compare to

        :return True:
            Versions equal
        :return False:
            Versions not equal
        """

        if other is None:
            return False

        if ((self.major != other.major) or
            (self.minor != other.minor) or
            (self.tick != other.tick)
        ):
            return False

        return True

    def __str__(self) -> str:
        """Creates a string of us

        :param self:
            Self

        :return str:
            Us
        """

        # If we have our integer fields, use those
        if (self.major is not None) and (self.minor is not None) and (self.tick is not None):
            return f"v{self.major}.{self.minor}.{self.tick}"

        # Else, if we have a name, use that
        if self.name is not None:
            return self.name

        # Uhhhh
        raise ValueError("Version has no identity")
