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

class Storage:
    """Google Cloud storage bucket
    """

    @staticmethod
    def _join(*args):
        """Joins cloud paths into a single string

        :param *args:
            Paths to join

        :return String:
            The joined paths
        """

        return "/".join(args)

    def __init__(self, id: str):
        """Creates a new cloud storage

        :param self:
            Self
        :param id:
            The storage ID to use

        :return none:
        """

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

    def upload(self, uploadPath, filePath):
        """Uploads a file to the cloud

        :param self:
            Self
        :param uploadPath:
            The path to upload the file to
        :param filePath:
            The file to upload

        :return True:
            File uploaded
        :return False:
            Failed to upload file
        """

        # Add our cloud ID to the full path
        uploadPath = Google.Storage._join(self._id, uploadPath)

        try:
            subprocess.check_output([
                "gsutil", "cp", "{}".format(filePath), "gs://{}".format(uploadPath)
            ])

        except subprocess.CalledProcessError:
            return False

        return True

    def list(self, path = None):
        """Lists files in the cloud

        :param self:
            Self
        :param path:
            The path to list from

        :return None:
            Failed to list files
        :return Array of Strings:
            Files at the path
        """

        if path == None:
            path = ""

        # Add our cloud ID to the full path
        path = Google.Storage._join(self.cloudId, path)

        try:
            output = subprocess.check_output([
                "gsutil", "ls", "gs://{}".format(path)
            ]).decode()

        except subprocess.CalledProcessError:
            return None

        stuff = []

        for thing in output.split("\n"):
            # If this was an empty line, skip it
            if len(thing) < 1:
                continue

            # Strip off the ugly gs:// and add this to the list
            stuff.append(thing.lstrip("gs://"))

        return stuff
