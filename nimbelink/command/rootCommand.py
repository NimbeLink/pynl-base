"""
A 'root' command

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import logging
import typing

from .command import Command

class RootCommand(Command):
    """A 'root' command

    A 'root' command acts as the initial entry point for the NimbeLink command
    stack. A 'root' command is expected -- and intended -- to handle any
    NimbeLink-specific setup operations, such as providing any universal command
    flags, logging setup, etc.

    This class is not intended to be instantiated directly -- that is, there
    should not be any object created of the RootCommand class:

        command = RootCommand(...)

    Rather, this class is intended to provide a single, command source for some
    common root command operations. It should be used like so:

        class MyCommand(RootCommand):
            ...

            def addArguments(...):
                super().addArguments(...)
                ...

            def runCommand(...):
                super().runCommand(...)
                ...

        command = MyCommand()

    If the command inheriting from RootCommand -- 'MyCommand' in the example
    above -- is only or mostly wrapping sub-commands, you do not need to
    implement addArguments() and/or runCommand() if you do not have
    MyCommand-specific actions to take.
    """

    def __init__(self, *args: typing.List[object], **kwargs: dict) -> None:
        """Creates a new 'root' command

        :param self:
            Self
        :param *args:
            Our positional arguments
        :param **kwargs:
            Our keyword arguments

        :return none:
        """

        super().__init__(*args, **kwargs)

        # Assume we'll need logging setup, knowing that if we're a sub-command
        # to a parent 'root' command that they'll change this for us
        self._setupLogging = True

        # Set all of our 'root' sub-commands to not initialize logging on their
        # own
        for subCommand in self._subCommands:
            if isinstance(subCommand, RootCommand):
                subCommand._setupLogging = False

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds arguments for our command

        :param self:
            Self
        :param parser:
            The parser to add arguments to

        :return none:
        """

        # If one of our parents is handling 'root' logging setup, skip it
        if not self._setupLogging:
            return

        parser.add_argument(
            "-v", "--verbose",
            dest = "rootVerbose",
            action = "count",
            default = 0,
            required = False,
            help = "Use verbose output (1 'warning', 2 'info', 3 'debug', 4 'extra debug')"
        )

    def runCommand(self, args: typing.List[object]) -> None:
        """Runs the root command

        :param self:
            Self
        :param args:
            Our arguments

        :return None:
            Command not handled
        """

        # If one of our parents is handling 'root' logging setup, skip it
        if not self._setupLogging:
            return None

        # Scale our logging verbosity according to the 'verbose' argument(s)
        if args.rootVerbose < 1:
            level = logging.ERROR
        elif args.rootVerbose < 2:
            level = logging.WARNING
        elif args.rootVerbose < 3:
            level = logging.INFO
        else:
            level = logging.DEBUG

        # Make a basic logging handler for all loggers
        #
        # This provides nice contextualized logging output for most modules.
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt = "%(asctime)s - %(module)s - %(levelname)s -- %(message)s"))

        logger = logging.getLogger()
        logger.setLevel(level)
        logger.addHandler(handler)

        # Set up logging for our base Command class
        logger = logging.getLogger(Command.LoggerNamespace)
        logger.addHandler(handler)
        logger.propagate = False

        if args.rootVerbose > 3:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.CRITICAL)

        return None
