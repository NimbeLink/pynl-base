"""
Google Cloud storage

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import subprocess
import typing

class Storage:
    """Google Cloud storage bucket
    """

    IdPrefix = "gs://"
    """What IDs are prefixed with"""

    @staticmethod
    def _join(*args) -> str:
        """Joins cloud paths into a single string

        :param *args:
            Paths to join

        :return str:
            The joined paths
        """

        return "/".join(args)

    def __init__(self, id: str) -> None:
        """Creates a new cloud storage

        :param self:
            Self
        :param id:
            The storage ID to use

        :return none:
        """

        # In case the ID has 'gs://' on the front, strip it
        if id.startswith(Storage.IdPrefix):
            id = id[len(Storage.IdPrefix):]

        self._id = id

    @property
    def id(self) -> str:
        """Gets our cloud ID

        :param self:
            Self

        :return str:
            The cloud ID
        """

        return self._id

    def _runCommand(self, command: typing.List[str]) -> bool:
        """Runs a Google Cloud command

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
            output = subprocess.check_output(["gsutil"] + command)

        except subprocess.CalledProcessError:
            return None

        return output.decode().rstrip()

    def upload(self, filePaths: str, uploadPath: str) -> bool:
        """Uploads a file to the cloud

        :param self:
            Self
        :param filePaths:
            The file(s) to upload
        :param uploadPath:
            The path to upload the file to

        :return True:
            File uploaded
        :return False:
            Failed to upload file
        """

        # Add our cloud ID to the full path
        uploadPath = Storage._join(self._id, uploadPath)

        output = self._runCommand(["cp"] + filePaths + ["gs://{}".format(uploadPath)])

        if output is None:
            return False

        return True

    def list(self, path: str = None) -> typing.List[str]:
        """Lists files in the cloud

        :param self:
            Self
        :param path:
            The path to list from

        :return None:
            Failed to list files
        :return Array of str:
            Files at the path
        """

        if path is None:
            path = ""

        # Add our cloud ID to the full path
        path = Storage._join(self._id, path)

        output = self._runCommand(["ls", "gs://{}".format(path)])

        if output is None:
            return None

        stuff = []

        for thing in output.split("\n"):
            # If this was an empty line, skip it
            if len(thing) < 1:
                continue

            # Strip off the ugly gs:// and add this to the list
            if thing.startswith(Storage.IdPrefix):
                thing = thing[len(Storage.IdPrefix):]

            stuff.append(thing)

        return stuff
