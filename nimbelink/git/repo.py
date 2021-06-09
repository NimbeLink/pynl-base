"""
Tools for working with Git

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import os
import subprocess
import tempfile
import typing

class Repo:
    """A Git repository
    """

    class RefType:
        """The type of Git thing a reference is
        """

        Commit  = 0
        Branch  = 1
        Tag     = 2

    class TagInfo:
        """Information about a Git tag
        """

        def __init__(self, name: str, commitHash: str) -> None:
            """Creates a Git tag info

            :param self:
                Self
            :param name:
                The name of the tag
            :param commitHash:
                The Git commit hash the tag is on

            :return none:
            """

            self.name = name
            self.commitHash = commitHash

    @staticmethod
    def _getEditor() -> str:
        """Gets the best editor to use for user input

        :param none:

        :return None:
            Failed to get editor
        :return str:
            The name of the editor
        """

        # First check to see if there's an editor defined locally for this
        # project
        try:
            editor = subprocess.check_output(["git", "config", "core.editor"])
        except subprocess.CalledProcessError:
            return None

        # If there was, use that
        if editor != "":
            return editor.decode().strip()

        # There wasn't a local Git editor for the project, so next see if
        # there's a global Git editor defined
        try:
            editor = subprocess.check_output(["git", "config", "--global", "core.editor"])
        except subprocess.CalledProcessError:
            return None

        # If there was, use that
        if editor != "":
            return editor.decode().strip()

        # Last case, try to use a global editor for the system
        os.environ.get("EDITOR")

        # If there was one, use that
        if editor != "":
            return editor

        # No other options left for finding an editor, so we failed
        return None

    def __init__(self, directory: str = None) -> None:
        """Creates a new Git repository

        :param self:
            Self
        :param directory:
            The directory the repo is in, if different than the current one

        :return none:
        """

        if directory is None:
            directory = os.getcwd()

        self._directory = directory

    @property
    def directory(self) -> str:
        """Gets the repository's local directory

        :param self:
            Self

        :return str:
            Our directory
        """

        return self._directory

    def _runCommand(self, command: typing.List[str]) -> str:
        """Runs a Git command in our repository

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
                "git",
                "-C",
                self._directory
            ] + command)

        except subprocess.CalledProcessError:
            return None

        return output.decode().rstrip()

    def getName(self, remoteName: str = "origin") -> str:
        """Gets the name of this repository

        :param self:
            Self
        :param remoteName:
            The name of the remote to use

        :return None:
            Failed to get name
        :return str:
            The name of the repository
        """

        # Get the remote URL
        remoteUrl = self._runCommand(["remote", "show", remoteName])

        # If that failed, that's a paddlin'
        if remoteUrl is None:
            return None

        # Get the name of the repo
        #
        # The URL will of course have '/' separating each field, with the last
        # being hte name of the repository. The repository's name might end with
        # '.git', so also strip that off.
        return remoteUrl.split("/")[-1].split(".")[0]

    def getBranch(self) -> str:
        """Gets the branch we're on

        :param self:
            Self

        :return None:
            Git repository not available
        :return str:
            The current branch
        """

        return self._runCommand(["rev-parse", "--abbrev-ref", "HEAD"])

    def getDescription(self, annotatedOnly: bool = True) -> str:
        """Gets a repository's Git description

        :param self:
            Self
        :param annotatedOnly:
            Only include the latest annotated tag

        :return None:
            Git repository description not available
        :return str:
            The Git repository description
        """

        commands = ["describe", "--always", "--long", "--dirty"]

        if not annotatedOnly:
            commands.append("--tags")

        return self._runCommand(commands)

    def getCommitHash(self, ref: str = "HEAD") -> str:
        """Gets the commit hash for a reference

        :param self:
            Self
        :param ref:
            The reference whose commit hash to get

        :return None:
            Failed to get commit hash
        :return str:
            The commit hash
        """

        return self._runCommand(["rev-parse", "{}^{{}}".format(ref)])

    def checkout(self, ref: str) -> bool:
        """Checks out a reference

        :param self:
            Self
        :param ref:
            The name of the reference to checkout

        :return True:
            Tag checked out
        :return False:
            Failed to check out tag
        """

        # Create a new annotated Git tag with our default subject
        output = self._runCommand(["checkout", "{}".format(ref)])

        if output is None:
            return False

        return True

    def getRefType(self, ref: str = "HEAD") -> int:
        """Gets a Git reference's type

        :param self:
            Self
        :param ref:
            The Git reference to check

        :return None:
            Failed to check reference type
        :return int:
            The Git reference type
        """

        output = self._runCommand(["show-ref", "--verify", "refs/tags/{}".format(ref)])

        if output is not None:
            return Repo.RefType.Tag

        output = self._runCommand(["show-ref", "--verify", "refs/heads/{}".format(ref)])

        if output is not None:
            return Repo.RefType.Branch

        return Repo.RefType.Commit

    def generateTag(
        self,
        name: str,
        commitHash: str = None,
        message: str = None,
        fileName: str = None,
        prompt: bool = False
    ) -> dict:
        """Generates a new Git tag

        If no method for getting a message is included, this will be a 'cheap'
        Git tag.

        :param self:
            Self
        :param name:
            The name of the tag
        :param commitHash:
            The hash to create the tag on
        :param message:
            The commit message to use
        :param fileName:
            A file containing the commit message
        :param propmt:
            Prompt to get a commit message

        :return None:
            Failed to generate tag
        :return Dictionary:
            The Git commit hash and name of the tag commit
        """

        # If they provided a message, prioritize that
        if message is not None:
            pass

        # Else, if they provided a file name, get the message from it
        elif fileName is not None:
            with open(fileName, "r") as messageFile:
                message = messageFile.read()

        # Else, if they want us to prompt for the message, do so
        elif prompt:
            # Write all of the text and launch an editor with a temporary file,
            # which we'll swipe the contents from for the tag's message
            with tempfile.NamedTemporaryFile(mode = "r+") as commitFile:
                # Launch the editor for the user to fill everything else out on
                # their own
                subprocess.check_call([
                    Repo._getEditor(),
                    commitFile.name
                ])

                # Go back to the start
                commitFile.seek(0)

                # Steal the text
                message = commitFile.read()

        commitCommands = ["tag", name]

        # If we have a specific commit to target, do so
        if commitHash is not None:
            commitCommands += ["{}".format(commitHash)]

        # If we have a message, make this an annotated tag
        #
        # Make sure any literal '#' characters are left alone by only cleaning
        # up whitespace. Otherwise Git will remove those, since it'll think
        # they're supposed to be comments.
        if message is not None:
            commitCommands += ["-a", "--cleanup=whitespace", "-m", "{}".format(message)]

        # Generate the tag
        output = self._runCommand(commitCommands)

        if output is None:
            return None

        # Get the commit hash of the commit we just tagged, and decode the
        # result of it and strip any line endings
        commitHash = self.getCommitHash(ref = name)

        if commitHash is None:
            return None

        return Repo.TagInfo(name = name, commitHash = commitHash)

    def doesTagExist(self, tagName: str) -> bool:
        """Checks if a tag exists

        :param self:
            Self
        :param tagName:
            The name of the tag to look for

        :return True:
            Tag exists
        :return False:
            Tag does not exist
        """

        # Try to list the tag
        tagList = self._runCommand(["tag", "-l", "{}".format(tagName)])

        if tagList is None:
            return False

        # If the tag wasn't listed, it doesn't exist
        if tagName not in tagList:
            return False

        return True

    def deleteTag(self, tagName: str) -> bool:
        """Deletes a Git tag

        :param self:
            Self
        :param tagName:
            The name of the tag to delete

        :return True:
            Tag deleted
        :return False:
            Failed to delete tag
        """

        # Create a new annotated Git tag with our default subject
        output = self._runCommand(["tag", "-d", "{}".format(tagName)])

        if output is None:
            return False

        return True
