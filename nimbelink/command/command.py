"""
A base command and sub-command

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import importlib
import logging
import sys
import textwrap
import typing

import nimbelink.utils as utils

class Command:
    """A west command for working with Skywire Nano devices, collected under the
    root 'skywire' command
    """

    LoggerNamespace = "_commands"
    """The root namespace for command loggers"""

    class SubCommand:
        """A sub-command for a base command
        """

        def __init__(self, moduleName: str, className: str) -> None:
            """Creates a new available sub-command

            :param self:
                Self
            :param moduleName:
                The module the class is found in
            :param className:
                The name of the class to import from the module

            :return none:
            """

            self.moduleName = moduleName
            self.className = className

        def getClass(self) -> object:
            """Gets the sub-command's class instance

            :param self:
                Self

            :return None:
                Failed to get class instance
            :return Class:
                The class instance
            """

            try:
                _module = importlib.import_module(self.moduleName)
                _class = getattr(_module, self.className)

                return _class

            except ImportError:
                return None

    @staticmethod
    def setupLogging() -> None:
        """Sets up basic logging for commands

        :param none:

        :return none:
        """

        # Get a logger for everything
        root = logging.getLogger()

        # If our logger already has handlers set up, don't bother adding our own
        # -- someone with more context has already set it up, or we've already
        # configured logging ourselves
        if root.hasHandlers():
            return

        # Everything gets 'info'-level logging
        root.setLevel(logging.INFO)

        # Make a handler for logging to standard output
        handler = logging.StreamHandler()

        # Add the handler to our root loggers
        root.addHandler(handler)

    @staticmethod
    def _generateDescription(description: str) -> str:
        """Generates a big string describing this command

        :param description:
            The description text

        :return str:
            The description string
        """

        # We likely have a description with a bunch of leading whitespace from a
        # multi-line string in the raw Python source, so let's first strip all
        # of that away
        fields = description.split("\n", maxsplit = 1)

        # If there is only one line, just use it
        if len(fields) < 2:
            return fields[0]

        # If there is a potential special case where the first line began
        # immediately after the triple quote, only unindent everything after
        # that line
        if fields[0] == fields[0].lstrip():
            description = fields[0] + "\n" + textwrap.dedent(fields[1])

        # Else, unindent everything together
        else:
            description = textwrap.dedent(description)

        # Next let's justify each line to our own standards
        #
        # Each line is separated by newline characters in the Python multi-line
        # string itself, so break the multi-line string into each individual
        # line.
        lines = description.split("\n")

        # We're going to be a little lazy with our appending and cleanup as we
        # form paragraphs, so make sure our space-removing step gets run on the
        # final paragraph by having an additional empty line to begin one final,
        # empty paragraph
        lines.append("")

        paragraphs = [""]

        # Next, the raw source code has its own justification, but that's not
        # necessarily aligned to the same boundary that we want to display in
        # the command's output on a terminal, so we'll need to collect each
        # paragraph
        #
        # So, let's string (ha) each line together into a single continuous
        # string that we can justify on our own.
        #
        # We'll note the end of a paragraph once we hit an entirely blank line,
        # and we'll combine each line by adding a space between them.
        for line in lines:
            # If this is an empty line, this is the end of the previous
            # paragraph
            if line == "":
                # We're going to append a space at the beginning of each
                # paragraph with our lazy appending below, so make sure we
                # remove that from each paragraph
                paragraphs[-1] = paragraphs[-1][1:]

                paragraphs.append("")

            # Else, got another line that applies to the current paragraph, so
            # append it
            else:
                paragraphs[-1] += " " + line

        text = ""

        # We've got our paragraphs, so let's finally output each line as it'll
        # appear on a terminal as a single string
        for paragraph in paragraphs:
            lines = textwrap.wrap(paragraph, 80)

            for line in lines:
                text += line + "\n"

            text += "\n"

        # Don't have additional excessive line endings at the beginning or end
        text = text.lstrip("\n").rstrip("\n")

        return text

    def __init__(
        self,
        name: str,
        help: str,
        description: str = None,
        subCommands: typing.Union["Command", "Command.SubCommand"] = None,
        needUsb: bool = False
    ) -> None:
        """Creates a new command

        Sub-commands can either be instantiated Command objects or they can be
        deferred Command.SubCommand classes, which will be instantiated during
        initialization.

        Usage of the Command.SubCommand class can aid in handling cases where
        not all sub-commands have dependencies met and might not be available,
        while still allowing the rest of the commands to run normally.

        :param self:
            Self
        :param name:
            The name of the Skywire command
        :param help:
            The short-form help text of the Skywire command
        :param description:
            The long-form description text of the Skywire command
        :param subCommands:
            Sub-commands that this command contains
        :param needUsb:
            Whether or not this command needs USB functionality

        :return none:
        """

        if description == None:
            description = help

        if subCommands == None:
            subCommands = []

        self._name = name
        self._help = help
        self._description = Command._generateDescription(description = description)

        self._subCommands = []

        for subCommand in subCommands:
            # If this is a deferred Command.SubCommand
            if isinstance(subCommand, Command.SubCommand):
                # Get the class
                subCommandClass = subCommand.getClass()

                # If the class doesn't exist, skip it
                if subCommandClass is None:
                    continue

                # It exists, so instantiate and append it
                self._subCommands.append(subCommandClass())

            # Else, append the already-instantiated object
            else:
                self._subCommands.append(subCommand)

        self._needUsb = needUsb

        self._logger = logging.getLogger(Command.LoggerNamespace + "." + self.__class__.__name__)

    def parseAndRun(self, args: typing.List[object] = None) -> int:
        """Runs a command with parameters

        :param self:
            Self
        :param args:
            Arguments for the command

        :return int:
            The result of the command
        """

        # Add our parameters and whatnot to a new parser
        parser = argparse.ArgumentParser(description = self._description)

        self._addArguments(parser = parser)

        # Parse the arguments using the parser we made
        #
        # If arguments weren't provided, argparse will use the system arguments.
        args = parser.parse_args(args = args)

        # Handle the arguments
        return self._runCommand(args = args)

    def _createParser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """Creates a parser

        :param self:
            Self
        :param parser:
            The parser adder

        :return parser:
            The root parser
        """

        # Make sure we keep our wonderful description's formatting by telling
        # the underlying argparse.ArgumentParser to use a formatter class of
        # 'raw'
        #
        # This should effectively mean all of our hard formatting work above is
        # left alone and printed to the console literally.
        return parser.add_parser(
            self._name,
            help = self._help,
            description = self._description,
            formatter_class = argparse.RawDescriptionHelpFormatter
        )

    def _addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds arguments to a parser

        :param self:
            Self
        :param parser:
            The parser to add arguments to

        :return none:
        """

        # First add this command's arguments
        try:
            self.addArguments(parser = parser)

        except NotImplementedError:
            pass

        # If we don't have sub-commands, nothing else to do
        if len(self._subCommands) < 1:
            return

        # Make a sub-parser for our sub-commands
        #
        # To avoid issues with nested sub-command users, make our sub-command
        # name argument unique to us.
        parser = parser.add_subparsers(
            title = "sub-commands",
            dest = f"{self._name}SubCommand",
            required = True
        )

        # For each of our command's sub-commands
        for subCommand in self._subCommands:
            # Add a new parser for this sub-command
            subParser = subCommand._createParser(parser = parser)

            # Add this sub-command's arguments
            subCommand._addArguments(parser = subParser)

    def _runCommand(self, args: typing.List[object]) -> int:
        """Runs the command

        :param self:
            Self
        :param args:
            Our known/expected arguments

        :return int:
            Our result
        """

        # If we will not be compatible with WSL's limited USB functionality and
        # we're running under WSL, elevate to PowerShell
        if self._needUsb and utils.Wsl.isWsl():
            return utils.Wsl.forward()

        try:
            # Always give the base command the chance to run
            try:
                result = self.runCommand(args)

            except NotImplementedError:
                result = None

            # If there was a result, use it as our final one
            if result is not None:
                return result

            # If we don't have any sub-commands, assume a successful result
            if len(self._subCommands) < 1:
                return 0

            # Get the name of the sub-command, which we made unique
            subCommandName = args.__getattribute__(f"{self._name}SubCommand")

            # Try to find a sub-command that'll run this
            for subCommand in self._subCommands:
                # If this is a matching sub-command, pass our arguments to it
                # for handling
                if subCommand._name == subCommandName:
                    return subCommand._runCommand(args = args)

            # We couldn't find this command somehow -- despite argparse passing
            # along to us -- so just use something as the error
            return 1

        except KeyboardInterrupt as ex:
            self.abortCommand()

            # Python seems to use a result of 1 as the keyboard interrupt result
            return 1

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        raise NotImplementedError(f"addArguments() not implemented by {self.__class__.__name__}")

    def runCommand(self, args: typing.List[object]) -> typing.Union[None, int]:
        """Runs the command

        Commands that do not have sub-commands should return an integer value
        indicating their result. If a command does not return a value -- that
        is, returns None -- and doesn't have sub-commands, the result will be
        assumed to be 0 (or successful). Error codes should follow the errno
        patterns.

        Commands that do have sub-commands can still return a final result in
        the form of an integer, but if they return a value of None their
        sub-commands will be run.

        :param self:
            Self
        :param args:
            Our known/expected arguments

        :return int:
            Command result
        :return None:
            Command not handled
        """

        raise NotImplementedError(f"runCommand() not implemented by {self.__class__.__name__}")

    def abortCommand(self) -> None:
        """Aborts the command

        :param self:
            Self

        :return none:
        """

        pass
