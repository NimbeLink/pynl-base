"""
Defines a version with components

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from .base import Base
from .info import Info

class Version:
    """A repository version

    The fullest form of the version looks like:

        v<major>.<minor>.<tick>-rc<rc>-<flavor>-<commit count>-g<commit>-dirty

    More concisely:

        vX.Y.Z-rcN-flavor-N-gAAAAAA-dirty

    'v' is optional

    -rc<rc> is optional in any version

    -<flavor> is optional in any version

    -dirty is optional in any version that includes the -g<commit>
    """

    @staticmethod
    def makeFromString(string: str) -> "Version":
        """Creates a new repository version from a string

        :param string:
            The string to parse

        :return None:
            Failed to parse version
        :return Version:
            The repository version
        """

        # Everything is separated by dashes
        fields = string.split("-")

        # If we don't have any fields, that's a paddlin'
        if len(fields) < 1:
            return None

        # Get our base version
        base = Base.makeFromString(string = fields[0])

        # If that failed, that's a paddlin'
        if base is None:
            return None

        # Drop the base
        string = "-".join(fields[1:])

        # If that's it, we've got our version
        if len(string) < 1:
            return Version(
                base = base
            )

        # If the next field looks like a release candidate iteration, grab it
        if string.startswith("rc"):
            # Get the release candidate iteration field from the string
            fields = string.split("-")

            # Parse the integer value, skipping over the 'rc' prefix
            try:
                rc = int(fields[0][2:])

            except ValueError:
                return None

            # Drop the release candidate iteration
            string = "-".join(fields[1:])

        else:
            rc = None

        # Get our Git info
        info, string = Info.pullFromString(string = string)

        # If there are more fields, assume they're flavoring and combine them
        # with '_' separating each one
        if len(string) > 0:
            fields = string.split("-")

            flavor = "_".join(fields)

        else:
            flavor = None

        # That's all we know how to parse
        return Version(
            base = base,
            rc = rc,
            flavor = flavor,
            info = info
        )

    def __init__(
        self,
        base: Base,
        rc: int = None,
        flavor: str = None,
        info: Info = None
    ) -> None:
        """Creates a new repository version

        :param self:
            Self
        :param base:
            The base version
        :param rc:
            The release candidate iteration
        :param flavor:
            Additional 'flavor' for the full version
        :param info:
            Git information

        :return none:
        """

        self.base = base
        self.rc = rc
        self.flavor = flavor
        self.info = info

    def __str__(self) -> str:
        """Gets a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        return self.toString()

    def increment(self, rc: bool = False, *args, **kwargs) -> None:
        """Increments a version

        :param self:
            Self
        :param rc:
            Increment the release candidate tick
        :param *args:
            Arguments for incrementing the base version
        :param **kwargs:
            Keyword arguments for incrementing the base version

        :return none:
        """

        if not rc:
            self.base.increment(*args, **kwargs)

            return

        if self.rc is None:
            raise TypeError("Cannot increment RC in non-RC version")

        self.rc += 1

    def toIntegers(self) -> str:
        """Creates am integer-based version string

        This format differs from the full string in that it's only the major,
        minor, tick, and 'build' (i.e. commit count) fields in a known format.

        :param self:
            Self

        :return str:
            A string representing us
        """

        # If our base doesn't have integer versions, just use a dumb default
        if self.base.isName():
            return "0.0.0+0"

        # Start with our base string, sans a leading 'v'
        string = f"{self.base}"[1:]

        # If we have commits, include the commit count as the 'build'
        if (self.info is not None) and (self.info.commits is not None):
            string += f"+{self.info.commits}"
        else:
            string += "+0"

        return string

    def toString(self) -> str:
        """Creates a full version string

        :param self:
            Self

        :return str:
            A string representing us
        """

        # Start with our base string
        string = f"{self.base}"

        # If we have flavor, add that
        if self.flavor is not None:
            string += f"-{self.flavor}"

        # If we're a release candidate, add that
        if self.rc is not None:
            string += f"-rc{self.rc}"

        # If we have Git info, add if
        if self.info is not None:
            string += f"-{self.info}"

        return string
