"""
A command for managing NimbeLink caching

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

import nimbelink.cache as cache
import nimbelink.command as command

class WhereCommand(command.Command):
    """A command for getting the cache backend location
    """

    def __init__(self) -> None:
        """Creates a new where command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "where",
            help = "Gets the cache location on the file system"
        )

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs the command

        :param self:
            Self
        :param args:
            Our arguments

        :return 0:
            Always
        """

        self.stdout.info(cache.getCache()._directory)

        return 0

class ListCommand(command.Command):
    """A command for listing cache items
    """

    def __init__(self) -> None:
        """Creates a new list command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "list",
            help = "Lists cached items and their values"
        )

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs the command

        :param self:
            Self
        :param args:
            Our arguments

        :return int:
            Our result
        """

        backend = cache.getCache().backend

        if backend is None:
            self.stdout.error("Failed to get cache backend")

            return 1

        for thing in backend:
            value = backend.get(thing)

            self.stdout.info(f"{thing}: {value}")

        return 0

class CacheCommand(command.Command):
    """A command for managing NimbeLink caching
    """

    def __init__(self) -> None:
        """Creates a new cache command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "cache",
            help = "Manages NimbeLink package caching",
            subCommands = [
                WhereCommand(),
                ListCommand()
            ]
        )

__commands__ = [
    CacheCommand()
]
"""The package's commands"""
