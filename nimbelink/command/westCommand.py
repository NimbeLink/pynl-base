"""
A command that can be used by the 'west' system

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import os
import sys
import typing
import west.commands

import nimbelink.config as config

from .command import Command

class WestCommand(Command, west.commands.WestCommand):
    """A command that can be used by the 'west' system
    """

    @staticmethod
    def setupImports(fileName: str, packageRoot: str) -> None:
        """Sets up import handling for west command scripts

        Because west likes to... take liberties... with how it runs commands,
        we'll have to work around their... interesting... decisions.

        :param fileName:
            The script whose import paths to set up
        :param packageRoot:
            The relative path to the root package

        :return none:
        """

        sys.path.insert(
            1,
            os.path.join(
                os.path.dirname(os.path.realpath(fileName)),
                packageRoot
            )
        )

    def __init__(self, *args, **kwargs) -> None:
        """Creates a new west command

        :param self:
            Self
        :param *args:
            Our positional arguments
        :param configuration:
            west-controlled configuration options
        :param **kwargs:
            Our keyword arguments

        :return none:
        """

        # Set up some basic logging for commands
        Command.setupLogging()

        # First pass our arguments to the NimbeLink command base
        Command.__init__(self, *args, **kwargs)

        # Next set up our west command
        west.commands.WestCommand.__init__(
            self,
            name = self._name,
            help = self._help,
            description = self._description
        )

    def do_add_parser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """Adds a new argument parser for our command

        :param self:
            Self
        :param parser:
            The parser to add to

        :return parser:
            The new parser
        """

        # Make a new parser
        parser = self._createParser(parser = parser)

        # Add our arguments to the parser
        self._addArguments(parser = parser)

        return parser

    def do_run(self, args: typing.List[object], unknownArgs: typing.List[object]) -> None:
        """Runs the command

        :param self:
            Self
        :param args:
            Our known/expected arguments
        :param unknownArgs:
            Our unknown arguments

        :return none:
        """

        self._runCommand(args = args)
