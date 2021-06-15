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
import re
import subprocess
import tempfile
import typing

from .host import Host
from . import version

class Repo:
    """A Git repository
    """

    ReleaseBranchPrefix = "release/"
    """The namespace for release branches in a Git repository"""

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

        self._host = None

    @property
    def directory(self) -> str:
        """Gets the repository's local directory

        :param self:
            Self

        :return str:
            Our directory
        """

        return self._directory

    @property
    def host(self) -> Host:
        """Gets our remote host

        :param self:
            Self

        :return Host:
            Our remote host
        """

        return self._host

    @host.setter
    def host(self, host) -> None:
        """Sets our remote host

        :param self:
            Self
        :param host:
            Our remote host

        :return none:
        """

        self._host = host
        self._host.repo = self

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

    def getBranch(self) -> str:
        """Gets the branch we're on

        :param self:
            Self

        :return None:
            Git repository not available
        :return str:
            The current branch
        """

        branch = self._runCommand(["rev-parse", "--abbrev-ref", "HEAD"])

        # If it looks like we aren't on a branch, then say this didn't work
        if branch == "HEAD":
            return None

        return branch

    def getDescription(self, annotatedOnly: bool = True, match: str = None) -> str:
        """Gets a repository's Git description

        :param self:
            Self
        :param annotatedOnly:
            Only include the latest annotated tag
        :param match:
            Tags to match against

        :return None:
            Git repository description not available
        :return str:
            The Git repository description
        """

        commands = ["describe", "--always", "--all", "--long", "--dirty"]

        if not annotatedOnly:
            commands += ["--tags"]

        if match is not None:
            commands += ["--match", match]

        description = self._runCommand(commands)

        # Make sure the descriptions doesn't have the 'heads/' or 'tags/'
        # prefixes, which comes from our '--all' flag
        if description.startswith("heads/"):
            description = description[len("heads/"):]

        if description.startswith("tags/"):
            description = description[len("tags/"):]

        return description

    def getCommitHash(self, ref: str = "HEAD", short: bool = False) -> str:
        """Gets the commit hash for a reference

        :param self:
            Self
        :param ref:
            The reference whose commit hash to get
        :param short:
            Whether or not to get the 'short' version of the hash

        :return None:
            Failed to get commit hash
        :return str:
            The commit hash
        """

        commands = ["rev-parse"]

        if short:
            commands += ["--short"]

        commands += ["{}^{{}}".format(ref)]

        return self._runCommand(commands)

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

    def getVersion(self, description: str = None) -> version.Version:
        """Creates a new repository version from the current repository

        :param self:
            Self
        :param description:
            The description to parse

        :return None:
            Failed to get version
        :return version.Version:
            The repository version
        """

        # Get our current branch
        branch = self.getBranch()

        # If we don't have a branch name, just use a default
        if branch is None:
            branch = "none"

        # If we're on a release branch
        if branch.startswith(Repo.ReleaseBranchPrefix):
            # Drop the 'release/'
            tagMatch = branch.replace(Repo.ReleaseBranchPrefix, "")

            # Get our Git description relative to the first release candidate
            # tag for this release branch
            #
            # We'll use a glob pattern for only including tags that fit within
            # this release branch.
            match = re.sub(pattern = r"\.x", repl = r".[0-9]*", string = tagMatch)

            # Specifically look for the first release candidate tag that matches
            # this pattern
            match += r"-rc1"

            description = self.getDescription(annotatedOnly = False, match = match)

            # If that failed, that's a paddlin'
            if description is None:
                return None

            # Make our version from that
            ver = version.Version.makeFromString(string = description)

            # Drop the release candidate designation
            ver.rc = None

            return ver

        # Else, we're on a development branch
        else:
            # Get our description
            description = self.getDescription()

            # If that failed, that's a paddlin'
            if description is None:
                return None

            # Make a version from that
            ver = version.Version.makeFromString(string = description)

            # Use our branch name as the base
            ver.base = version.Base(name = branch)

            # Cool cool cool
            return ver
