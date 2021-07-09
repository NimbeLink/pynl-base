"""
Gets versions

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import os
import typing

import nimbelink.command as command
import nimbelink.git as git

from .base import Base
from .version import Version

class VersionCommand(command.Command):
    """A command for generating version information
    """

    def __init__(self) -> None:
        """Creates a new version command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "version",
            help = "generates version information",
            description =
                """This tool will generate version information for a repository.
                """
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds our arguments to a parser

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        parser.add_argument(
            "-d", "--directory",
            required = False,
            help = "The directory to get the version of"
        )

        parser.add_argument(
            "-b", "--base",
            required = False,
            help = "Specify the base ('v.x.y.z') version string manually"
        )

        parser.add_argument(
            "-f", "--flavor",
            required = False,
            help = "Specify the flavor of the version"
        )

        parser.add_argument(
            "-s", "--string",
            required = False,
            help = "Specify the entire version string manually"
        )

        parser.add_argument(
            "-t", "--type",
            required = False,
            choices = [
                "str",
                "int"
            ],
            default = "str",
            help = "Generate an integer or string version"
        )

        parser.add_argument(
            "-o", "--output",
            dest = "outputFile",
            required = False,
            help = "Output file name; if not provided, stdout used instead"
        )

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs the version generation script

        :param self:
            Self
        :param args:
            Our arguments

        :return int:
            Our result
        """

        # If the version has been specified, use it
        if args.string is not None:
            version = Version.makeFromString(string = args.string)

            # If that failed, that's a paddlin'
            if version is None:
                self.stdout.error(f"Failed to make a version from '{args.string}'")
                return 1

        # Else, get the current repository version
        else:
            # Make a version from the repo's Git description
            version = git.Repo(directory = args.directory).getVersion()

            # If that failed, that's a paddlin'
            if version is None:
                self.stdout.error(f"Failed to make version for '{args.directory}'")
                return 1

            # If they specified the base version, use that
            if args.base is not None:
                version.base = Base(name = args.base)

            # If they specified the flavor, use that
            if args.flavor is not None:
                version.flavor = args.flavor

        # If this is an app version file, format for that
        if args.type == "str":
            contents = version.toString()

            # If this will be going to a file for compilation in an
            # application, make sure it's a C-style string
            if args.outputFile is not None:
                contents = f"\"{contents}\""

        # Else, if this is an MCUBoot version file, format for that
        elif args.type == "int":
            contents = version.toIntegers()

        # Else, huh?
        else:
            raise Exception(f"Invalid version type '{args.type}'")

        # If this isn't going to a directory, just spit it
        if not args.outputFile:
            print(f"{contents}")
            return 0

        try:
            # If the file exists
            if os.path.exists(args.outputFile):
                with open(args.outputFile, "r") as file:
                    # If the contents are the same, nothing to do
                    if file.read().strip() == contents:
                        return 0

                # The file is different, so delete it first
                os.remove(args.outputFile)

        except OSError:
            pass

        # Write out the contents
        with open(args.outputFile, "w+") as file:
            file.write(contents)

        return 0
