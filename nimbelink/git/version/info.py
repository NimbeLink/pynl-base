"""
Git information

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

class Info:
    """Git information
    """

    @staticmethod
    def pullFromString(string: str) -> typing.Tuple["Info", str]:
        """Creates a new Git info from a string

        :param string:
            The string to parse

        :raise ValueError:
            Invalid version string

        :return typing.Tuple[Info, str]:
            The Git info and any remaining string
        """

        # Everything is separated by dashes
        fields = string.split("-")

        # If there is a dirty flag
        if fields[-1] == "dirty":
            # Note it
            dirty = True

            # Drop the dirty
            fields = fields[:-1]

        else:
            dirty = False

        # If there is a Git commit
        if fields[-1].startswith("g"):
            # Note it
            commitHash = fields[-1][1:]

            # Drop the commit
            fields = fields[:-1]

        else:
            commitHash = None

        # If there was a Git commit, expect a commit count
        if commitHash is not None:
            # Grab the commit count
            try:
                commits = int(fields[-1])
            except ValueError:
                raise ValueError(f"Could not parse '{string}' into a version")

            # Drop the commit count
            fields = fields[:-1]

        else:
            commits = None

        # If we had a dirty without a commit, that's a paddlin'
        if dirty and (commitHash is None):
            raise ValueError(f"Could not parse '{string}' into a version")

        return (
            Info(
                commits = commits,
                commitHash = commitHash,
                dirty = dirty
            ),
            "-".join(fields)
        )

    def __init__(self, commits: int, commitHash: str, dirty: bool = False) -> None:
        """Creates a new Git information

        :param self:
            Self
        :param commits:
            Commit count since last tag
        :param commitHash:
            The current commit hash
        :param dirty:
            Whether or not the repository is dirty

        :return none:
        """

        self.commits = commits
        self.commitHash = commitHash
        self.dirty = dirty

    def __str__(self) -> str:
        """Creates a string of us

        :param self:
            Self

        :return str:
            Us
        """

        string = ""

        if self.commits is not None:
            string += f"-{self.commits}"

        if self.commitHash is not None:
            string += f"-g{self.commitHash}"

        if self.dirty:
            string += "-dirty"

        # Make sure we skip over the leading '-' character
        return string[1:]
