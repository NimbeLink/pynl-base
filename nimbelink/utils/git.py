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

class Git:
    """Tools for using Git
    """

    class TagInfo:
        """Information about a Git tag
        """

        def __init__(self, name, commitHash):
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
    def getBranch(directory = None):
        """Gets the branch we're on

        :param directory:
            The directory containing the repository

        :return None:
            Git repository not available
        :return String:
            The current branch
        """

        if directory == None:
            try:
                directory = os.getcwd()
            except OSError:
                return None

        try:
            branch = subprocess.check_output([
                "git", "-C", directory, "rev-parse", "--abbrev-ref", "HEAD"
            ])

        except subprocess.CalledProcessError:
            return None

        return branch.decode().strip()

    @staticmethod
    def getRepoDescription(directory = None, annotatedOnly = True):
        """Gets a repository's Git description

        :param directory:
            The directory containing the repository
        :param annotatedOnly:
            Only include the latest annotated tag

        :return None:
            Git repository description not available
        :return String:
            The Git repository description
        """

        if directory == None:
            try:
                directory = os.getcwd()
            except OSError:
                return None

        commands = ["git", "-C", directory, "describe", "--always", "--long", "--dirty"]

        if not annotatedOnly:
            commands.append("--tags")

        try:
            description = subprocess.check_output(commands)

        except subprocess.CalledProcessError:
            return None

        return description.decode().strip()

    @staticmethod
    def _getEditor():
        """Gets the best editor to use for user input

        :param none:

        :return None:
            Failed to get editor
        :return String:
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

    @staticmethod
    def getCommitHash(ref = "HEAD"):
        """Gets the commit hash for a reference

        :param ref:
            The reference whose commit hash to get

        :return None:
            Failed to get commit hash
        :return String:
            The commit hash
        """

        try:
            return subprocess.check_output([
                "git", "rev-parse", "{}^{{}}".format(ref)
            ]).decode().strip()

        except subprocess.CalledProcessError:
            return None

    @staticmethod
    def generateTag(name, commitHash = None, message = None, fileName = None, prompt = False):
        """Generates a new Git tag

        If no method for getting a message is included, this will be a 'cheap'
        Git tag.

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
        if message != None:
            pass

        # Else, if they provided a file name, get the message from it
        elif fileName != None:
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
                    Git._getEditor(),
                    commitFile.name
                ])

                # Go back to the start
                commitFile.seek(0)

                # Steal the text
                message = commitFile.read()

        commitCommands = ["git", "tag", name]

        # If we have a specific commit to target, do so
        if commitHash != None:
            commitCommands += ["{}".format(commitHash)]

        # If we have a message, make this an annotated tag
        #
        # Make sure any literal '#' characters are left alone by only cleaning
        # up whitespace. Otherwise Git will remove those, since it'll think
        # they're supposed to be comments.
        if message != None:
            commitCommands += ["-a", "--cleanup=whitespace", "-m", "{}".format(message)]

        # Generate the tag
        try:
            subprocess.check_output(commitCommands)

        except subprocess.CalledProcessError:
            print("Failed to make new Git tag")
            return None

        # Get the commit hash of the commit we just tagged, and decode the
        # result of it and strip any line endings
        commitHash = Git.getCommitHash(ref = name)

        if commitHash == None:
            print("Failed to get Git commit hash for tagged commit")
            return None

        return Git.TagInfo(name = name, commitHash = commitHash)

    @staticmethod
    def doesTagExist(tagName):
        """Checks if a tag exists

        :param tagName:
            The name of the tag to look for

        :return True:
            Tag exists
        :return False:
            Tag does not exist
        """

        # Try to list the tag
        try:
            tagList = subprocess.check_output([
                "git", "tag", "-l", "{}".format(tagName)
            ])

        except subprocess.CalledProcessError:
            print("Failed to check for tag existing")
            return False

        # If the tag wasn't listed, it doesn't exist
        if tagName not in tagList.decode().strip():
            return False

        return True

    @staticmethod
    def checkoutTag(tagName):
        """Checks out a Git tag

        :param tagName:
            The name of the tag to checkout

        :return True:
            Tag checked out
        :return False:
            Failed to check out tag
        """

        # Create a new annotated Git tag with our default subject
        try:
            subprocess.check_output([
                "git", "checkout", "{}".format(tagName)
            ])

        except subprocess.CalledProcessError:
            print("Failed to checkout Git tag")
            return False

        return True

    @staticmethod
    def deleteTag(tagName):
        """Deletes out a Git tag

        :param tagName:
            The name of the tag to delete

        :return True:
            Tag deleted
        :return False:
            Failed to delete tag
        """

        # Create a new annotated Git tag with our default subject
        try:
            subprocess.check_output([
                "git", "tag", "-d", "{}".format(tagName)
            ])

        except subprocess.CalledProcessError:
            print("Failed to delete Git tag")
            return False

        return True
