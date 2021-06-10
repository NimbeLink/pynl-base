"""
A remote Git repository host

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import subprocess
import typing

class Host:
    """A remote Git repository host
    """

    class Credentials:
        """Credentials for Git operations
        """

        def __init__(self, username: str, password: str) -> None:
            """Creates new Git credentials

            :param self:
                Self
            :param username:
                The login username
            :param password:
                The login password

            :return none:
            """

            self.username = username
            self.password = password

    def __init__(self, name: str) -> None:
        """Creates a new host

        :param self:
            Self
        :param name:
            The remote name of this repository

        :return none:
        """

        self._name = name
        self._remote = "origin"

        username = self._runCommand(["config", "--global", "user.name"])
        password = self._runCommand(["config", "--global", "user.password"])

        if (username is not None) and (password is not None):
            self._credentials = Host.Credentials(
                username = username,
                password = password
            )
        else:
            self._credentials = None

    def _runCommand(self, command: typing.List[str]) -> str:
        """Runs a Git command

        :param self:
            Self
        :param command:
            The command and its arguments

        :return None:
            Command failed
        :return str:
            The successful command's output
        """

        try:
            output = subprocess.check_output([
                "git"
            ] + command)

        except subprocess.CalledProcessError:
            return None

        return output.decode().rstrip()

    @property
    def credentials(self) -> "Host.Credentials":
        """Gets our Git credentials

        :param self:
            Self

        :return None:
            No credentials configured
        :return str:
            Our credentials
        """

        return self._credentials

    @credentials.setter
    def credentials(self, credentials: "Host.Credentials") -> None:
        """Sets Git credentials for automatic usage

        :param credentials:
            The Git credentials to cache

        :raise RuntimeError:
            Failed to cache credentials

        :return none:
        """

        if not (self._runCommand(["config", "--global", "user.name", credentials.username]) or
                self._runCommand(["config", "--global", "user.password", credentials.password])
        ):
            raise RuntimeError("Failed to configure Git credentials")

        self._credentials = credentials

    @property
    def remote(self) -> str:
        """Gets the repository's remote name in the local Git repository

        :param self:
            Self

        :return str:
            Our remote name
        """

        return self._remote

    @property
    def name(self) -> str:
        """Gets the name of this repository

        :param self:
            Self

        :return None:
            Failed to get name
        :return str:
            The name of the repository
        """

        return self._name
