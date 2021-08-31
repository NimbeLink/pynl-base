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
import importlib
import typing

import nimbelink.command as command
import nimbelink.module as module

class ListCommand(command.Command):
    """A command for listing NimbeLink packages
    """

    def __init__(self) -> None:
        """Creates a new list command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "list",
            help = "lists available NimbeLink Python packages"
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

        self.stdout.info("Available Modules:")

        for submodule in module.__modules__:
            try:
                # Try to import the module that may or may not be locally available
                importlib.import_module(name = submodule.name)

                self.stdout.info(f"    '{submodule.name}' (alias '{submodule.alias}')")

            except ImportError as ex:
                continue

class ModuleCommand(command.Command):
    """A command for managing NimbeLink packages
    """

    def __init__(self) -> None:
        """Creates a new module command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "module",
            help = "provides NimbeLink Python package functionality",
            description =
                """Handles NimbeLink Python packages
                """,
            subCommands = [ListCommand()]
        )
