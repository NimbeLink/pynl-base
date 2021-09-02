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

        for submodule in module.__modules__:
            try:
                # Try to import the module that may or may not be locally available
                importlib.import_module(name = submodule.name)

                self.stdout.info(submodule)

            except ImportError as ex:
                continue

class RegisterCommand(command.Command):
    """A command for registering a NimbeLink package
    """

    def __init__(self) -> None:
        """Creates a new register command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "register",
            help = "registers a NimbeLink Python package"
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds our arguments

        :param self:
            Self
        :param parser:
            The parser to add arguments to

        :return none:
        """

        parser.add_argument(
            "-a", "--alias",
            help = "The name for the module when made available within the 'nimbelink' package"
        )

        parser.add_argument(
            "-p", "--package",
            help = "The standalone name of the package"
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

        submodule = module.Module(name = args.package, alias = args.alias)

        module.register(submodule)

        self.stdout.info(f"Registered '{submodule}')")

        return 0

class UnregisterCommand(command.Command):
    """A command for unregistering a NimbeLink package
    """

    def __init__(self) -> None:
        """Creates a new unregister command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "unregister",
            help = "unregisters a NimbeLink Python package"
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds our arguments

        :param self:
            Self
        :param parser:
            The parser to add arguments to

        :return none:
        """

        parser.add_argument(
            "-a", "--alias",
            help = "The name for the module when made available within the 'nimbelink' package"
        )

        parser.add_argument(
            "-p", "--package",
            help = "The standalone name of the package"
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

        submodule = module.Module(name = args.package, alias = args.alias)

        if submodule not in module.__modules__:
            self.stdout.error(f"Failed to find package '{submodule.name}'")

            return 1

        module.unregister(submodule)

        self.stdout.info(f"Unregistered '{submodule}')")

        return 0

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
            subCommands = [
                ListCommand(),
                RegisterCommand(),
                UnregisterCommand()
            ]
        )
