"""
Tools for working with west

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import os
import subprocess
import sys
import typing

import nimbelink.git as git

class West:
    """Tools for working with west
    """

    @staticmethod
    def _runCommand(command: typing.List[str], redirect: bool = False) -> bool:
        """Runs a west command

        :param command:
            The command and its arguments
        :param redirect:
            Redirect output to stdout and stderr

        :return None:
            Command failed
        :return str:
            The successful command's output
        """

        try:
            if redirect:
                subprocess.check_call(
                    ["west"] + command,
                    stdout = sys.stdout,
                    stderr = sys.stderr
                )

                # There isn't any output, so indicate a success with an empty
                # string
                return ""

            else:
                output = subprocess.check_output(
                    ["west"] + command
                )

        except subprocess.CalledProcessError:
            return None

        return output.decode().rstrip()

    @staticmethod
    def init(host: git.Host, ref: str = None) -> bool:
        """Initializes a new west environment

        :param host:
            The remote repository to check out and use
        :param ref:
            The Git reference to check out

        :return True:
            West initialized
        :return False:
            Failed to initialize west
        """

        commands = ["init", "-m", host.url]

        if ref is not None:
            commands += ["--mr", ref]

        # Initialize the repository
        output = West._runCommand(commands)

        if output is None:
            return False

        return True

    @staticmethod
    def update() -> bool:
        """Updates the west environment's dependencies

        :param none:

        :return True:
            West updated
        :return False:
            Failed to update west
        """

        # Cheaply update the dependencies
        output = West._runCommand(["update", "--narrow", "--fetch-opt=--depth=1"])

        if output is None:
            return False

        return True

    @staticmethod
    def checkManifest() -> bool:
        """Makes sure the repository's dependent repositories are in their
        final state

        :param none:

        :return True:
            Repositories ready
        :return False:
            Repositories were not ready
        """

        # Get the current manifest
        first = West._runCommand(["list"])

        if first is None:
            return False

        # Update the dependent repositories
        output = West._runCommand(["update"])

        if output is None:
            return False

        # Get the manifest after the update
        second = West._runCommand(["list"])

        if second is None:
            return False

        # If anything changed, that's a paddlin'
        if first != second:
            return False

        return True

    @staticmethod
    def getMainDirectory() -> str:
        """Gets the main manifest directory

        :param none:

        :return None:
            Failed to get directory
        :return str:
            The main repository directory
        """

        # Get the top-level directory
        toplevel = West._runCommand(["topdir"])

        # If that failed, that's a paddlin'
        if toplevel is None:
            return None

        # Get the list of repositories
        list = West._runCommand(["list"])

        # If that failed, that's a paddlin'
        if list is None:
            return None

        # Split the response into each line
        list = list.split("\n")

        manifest = None

        # Find the 'manifest' line
        #
        # It's typically the first line, but we might as well just dynamically
        # find it.
        for repo in list:
            fields = repo.split()

            # If this is the line, combine its relative directory with our
            # topdir for the full path
            if fields[0] == "manifest":
                return os.path.join(toplevel, fields[1])

        # We must not have found it
        return None

    @staticmethod
    def build(pristine: bool = False, definitions: dict = None) -> bool:
        """Performs a build

        :param pristine:
            Whether or not the build should be pristine
        :param version:
            A version to manually specify

        :return True:
            Build done
        :return False:
            Failed to finish build
        """

        # Get the main repository's directory
        buildDirectory = West.getMainDirectory()

        # If that failed, that's a paddlin'
        if buildDirectory is None:
            return False

        previousDirectory = os.getcwd()

        # Build from that directory
        os.chdir(buildDirectory)

        command = ["build"]

        # If we are doing a pristine build, add that flag
        if pristine:
            command += ["--pristine"]

        # If there are additional definitions specified, include them
        if (definitions is not None) and (len(definitions) > 0):
            command += ["--"]

            for definition, value in definitions.items():
                command += [f"-D{definition}={value}"]

        # Build!
        result = West._runCommand(command, redirect = True)

        # Go back to our previous directory
        os.chdir(previousDirectory)

        if result is None:
            return False

        return True
