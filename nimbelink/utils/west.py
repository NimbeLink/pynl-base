"""
Tools for working with west

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import subprocess
import sys
import typing

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
    def build(pristine: bool, version: str = None) -> bool:
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

        command = ["build"]

        if pristine:
            command += ["--pristine"]

        if version is not None:
            command += ["--", "-DNIMBELINK_VERSION={}".format(version)]

        result = West._runCommand(command, redirect = True)

        if result is None:
            return False

        return True
