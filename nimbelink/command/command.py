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
import inspect
import logging
import sys
import textwrap
import typing

from .wsl import Wsl

class Command:
    """A west command for working with Skywire Nano devices, collected under the
    root 'skywire' command
    """

    LoggerNamespace = "_commands"
    """The root namespace for command loggers"""

    @staticmethod
    def _getParagraphs(string: str) -> typing.List[str]:
        """Gets paragraph strings from formatted text

        :param string:
            The string to parse

        :return typing.List[str]:
            The paragraph strings
        """

        # We likely have a string with a bunch of leading whitespace from a
        # multi-line string in the raw Python source, so let's first strip all
        # of that away
        fields = string.split("\n", maxsplit = 1)

        # If there is only one line, just use it
        if len(fields) < 2:
            return fields[0]

        # If this is the special case where the first line began immediately
        # after the triple quote -- on the same line -- only unindent everything
        # after that line
        #
        # Otherwise our unindenting calculations will not result in any
        # following lines being unindented correctly.
        if fields[0] == fields[0].lstrip():
            string = fields[0] + "\n" + textwrap.dedent(fields[1])

        # Else, unindent everything together
        else:
            string = textwrap.dedent(string)

        # Next let's justify each line to our own standards
        #
        # Each line is separated by newline characters in the Python multi-line
        # string itself, so break the multi-line string into each individual
        # line.
        lines = string.split("\n")

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

        return paragraphs

    @staticmethod
    def _combineParagraphs(paragraphs: typing.List[str], columns: int = 80) -> str:
        """Generates a big string from paragraphs

        :param paragraphs:
            The paragraphs to use
        :param columns:
            How many columns to justify to

        :return str:
            The string
        """

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
        name: str = None,
        help: str = None,
        description: str = None,
        subCommands: typing.List["Command"] = None,
        needUsb: bool = False
    ) -> None:
        """Creates a new command

        Sub-commands can either be pre-instantiated objects, classes that can be
        default-instantiated (i.e. don't take arguments in __init__), or lambdas
        that don't have arguments.

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

        :raise Exception:
            Failed to auto-fill command name or help text

        :return none:
        """

        # If we aren't given a name specifically, try to generate one from the
        # child class' name
        if name is None:
            # Remove any casing
            name = self.__class__.__name__.lower()

            # Strip a 'command' post-fix in the class name
            if name.endswith("command"):
                name = name[:-len("command")]

            # If we weren't given anything to work with, that's a paddlin'
            if len(name) < 1:
                raise Exception("Cannot have an auto-filled command name if class is just 'Command'")

        # If we aren't given help text, try to generate some from the child
        # class' doc strings
        if help is None:
            # If the class has doc strings
            if self.__class__.__doc__ is not None:
                paragraphs = Command._getParagraphs(string = self.__class__.__doc__)

                # Use the first paragraph as our help text
                help = paragraphs[0]

                # If we weren't given a description either, try to make a more
                # informed decision about what doc string contents to use
                if description is None:
                    # If there is more than one paragraph, treat the first one
                    # as a subject for the help text and use the rest as the
                    # more in-depth description text
                    if len(paragraphs) > 1:
                        description = Command._combineParagraphs(
                            paragraphs = paragraphs[1:]
                        )
                    # Else, just use the same text as the help
                    else:
                        description = Command._combineParagraphs(
                            paragraphs = paragraphs
                        )

            # Else, we weren't given anything to work with, and that's a
            # paddlin'
            else:
                raise Exception("Cannot have an auto-filled command help if class has no doc string")

        # If we aren't given a description, try to generate some from the child
        # class' doc strings
        if description is None:
            # If the class has doc strings, use them for the description
            if self.__class__.__doc__ is not None:
                description = Command._combineParagraphs(
                    paragraphs = Command._getParagraphs(string = self.__class__.__doc__)[1:]
                )

            # Else, just re-use the help text
            else:
                description = help

        else:
            description = Command._combineParagraphs(
                paragraphs = Command._getParagraphs(string = description)
            )

        if subCommands is None:
            subCommands = []

        self._name = name
        self._help = help
        self._description = description

        # Assume we're the 'root' command
        self._isRoot = True

        for i in range(len(subCommands)):
            # If this is a class or a lambda, make the sub-command
            #
            # Otherwise, this must be an already-instantiated object, so
            # obviously don't re-instantiate it.
            if inspect.isclass(subCommands[i]) or inspect.isfunction(subCommands[i]):
                subCommands[i] = subCommands[i]()

                self.__logger.debug(f"Instantiated sub-command '{subCommands[i]._name}'")

            # None of our sub-commands can be a 'root' command, since they're
            # under us
            subCommands[i]._isRoot = False

        self._subCommands = subCommands

        self._needUsb = needUsb

        # Get a logger for logging our own command stuff
        #
        # This is distinct from the sans-formatting output a typical command
        # will generate.
        #
        # We'll also isolate our logger from other loggers, since someone might
        # library debugging output but still not want the boring command
        # handling logging.
        self.__logger = logging.getLogger(Command.LoggerNamespace + "." + self.__class__.__name__)

        self._stdout = None

        commandLogger = logging.getLogger("nimbelink-commands")

        # If we haven't yet, set up command output using a standard 'stream'
        # logger
        #
        # We'll do this check in case someone did a poor job managing their
        # __init__ chain with their parent class(es).
        if not commandLogger.hasHandlers():
            handler = logging.StreamHandler(stream = sys.stdout)
            handler.setFormatter(logging.Formatter(fmt = "%(message)s"))

            commandLogger.setLevel(logging.DEBUG)
            commandLogger.addHandler(handler)
            commandLogger.propagate = False

    @property
    def _allSubCommands(self) -> "Command":
        """Gets all downstream sub-commands

        This will also result in sub-commands of sub-commands being returned.

        :param self:
            Self

        :yield Command:
            The next sub-command

        :return none:
        """

        for subCommand in self._subCommands:
            # First yield the sub-command itself
            yield subCommand

            # Next yield all of the sub-command's sub-commands
            for subSubCommand in subCommand._allSubCommands:
                yield subSubCommand

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
        return self._run(args = args)

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

        # If we're the 'root' command, add some top-level stuff
        if self._isRoot:
            parser.add_argument(
                "-v", "--verbose",
                dest = "rootVerbose",
                action = "count",
                default = 0,
                required = False,
                help = "Use verbose output (1 'warning', 2 'info', 3 'debug', 4 'extra debug')"
            )

            if Wsl.isWsl():
                help = "Force keeping operation inside WSL, even if using USB"
            else:
                help = argparse.SUPPRESS

            parser.add_argument(
                "-w", "--force-wsl",
                dest = "forceWsl",
                action = "count",
                default = 0,
                required = False,
                help = help
            )

        # First add this command's arguments
        try:
            self.addArguments(parser = parser)

            self.__logger.debug("Added self-arguments")

        except NotImplementedError:
            pass

        # If we don't have sub-commands, nothing else to do
        if len(self._subCommands) < 1:
            self.__logger.debug("No sub-commands, done with arguments")

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
            self.__logger.debug(f"Adding sub-command '{subCommand._name}' arguments")

            # Add a new parser for this sub-command
            subParser = subCommand._createParser(parser = parser)

            # Add this sub-command's arguments
            subCommand._addArguments(parser = subParser)

    def _run(self, args: typing.List[object]) -> int:
        """Runs the command

        :param self:
            Self
        :param args:
            Our arguments

        :return int:
            Our result
        """

        # If we're the 'root' command, handle the top-level stuff
        if self._isRoot:
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

        try:
            return self._runCommand(args = args)

        except KeyboardInterrupt as ex:
            self.__logger.debug("Keyboard interrupt")

            # Python seems to use a result of 1 as the keyboard interrupt result
            return 1

    def _runCommand(self, args: typing.List[object]) -> int:
        """Runs the command

        :param self:
            Self
        :param args:
            Our arguments

        :return int:
            Our result
        """

        # If we will not be compatible with WSL's limited USB functionality,
        # we're running under WSL, and we're allowed to do so, elevate to
        # PowerShell
        if self._needUsb and Wsl.isWsl() and not args.forceWsl:
            self.__logger.debug("Command run under WSL but needs USB, elevating to PowerShell")

            return Wsl.forward()

        try:
            # Always give the base command the chance to run
            try:
                self.__logger.debug("Running command")

                result = self.runCommand(args)

            except NotImplementedError:
                self.__logger.debug("runCommand not implemented, assuming pass-through")

                result = None

            # If there was a result, use it as our final one
            if result is not None:
                self.__logger.debug(f"Command handled ({result})")

                return result

            # If we don't have any sub-commands, assume a successful result
            if len(self._subCommands) < 1:
                self.__logger.debug("No sub-commands, assuming successful")

                return 0

            # Get the name of the sub-command, which we made unique
            subCommandName = args.__getattribute__(f"{self._name}SubCommand")

            # Try to find a sub-command that'll run this
            for subCommand in self._subCommands:
                # If this is a matching sub-command, pass our arguments to it
                # for handling
                if subCommand._name == subCommandName:
                    self.__logger.debug(f"Passing downstream to sub-command '{subCommand._name}'")

                    return subCommand._runCommand(args = args)

            self.__logger.debug(f"No matching sub-command found for '{subCommandName}'")

            # We couldn't find this command somehow -- despite argparse passing
            # along to us -- so just use something as the error
            return 1

        except Exception as ex:
            self.__logger.exception(ex)

            self.__logger.debug("Aborting command")

            # Allow handling command issues
            self.abortCommand(args = args, exception = ex)

            # In the event we're someone's sub-command, keep bubbling the
            # exception up to make sure everyone gets a chance to handle the
            # aborted command
            raise ex

    @property
    def stdout(self) -> logging.Logger:
        """Gets this command's stdout

        :param self:
            Self

        :return logging.Logger:
            This command's logger
        """

        if self._stdout is None:
            self._stdout = logging.getLogger("nimbelink-commands." + self.__class__.__name__)

        return self._stdout

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
            Our arguments

        :return int:
            Command result
        :return None:
            Command not handled
        """

        raise NotImplementedError(f"runCommand() not implemented by {self.__class__.__name__}")

    def abortCommand(self, args: typing.List[object], exception: Exception = None) -> None:
        """Aborts the command

        :param self:
            Self
        :param exception:
            The exception that occurred, if any

        :return none:
        """

        pass
