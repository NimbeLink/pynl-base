"""
The main entry point for NimbeLink package management

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import typing

import nimbelink.command as command

from nimbelink.modules.module import Module
from nimbelink.modules.knownModules import KnownModules

class ListCommand(command.Command):
    """A command for listing NimbeLink-provided packages
    """

    def __init__(self) -> None:
        """Creates a new NimbeLink command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "list",
            help = "lists available NimbeLink Python packages"
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        pass

    def runCommand(self, args: typing.List[object]) -> None:
        """Runs the command

        :param self:
            Self
        :param args:
            Our arguments

        :return none:
        """

        for module in KnownModules:
            try:
                module.importModule()
                print("Found module '{}'".format(module.name))

            except ImportError:
                continue

class ModuleCommand(command.Command):
    """A command for managing NimbeLink-provided packages
    """

    def __init__(self) -> None:
        """Creates a new NimbeLink command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "mod",
            help = "provides NimbeLink Python package functionality",
            description =
                """Handles NimbeLink Python packages
                """,
            subCommands = [ListCommand()]
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        pass
