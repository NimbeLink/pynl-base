"""
Archives for application artifacts

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import os
import shutil

import nimbelink.cloud.google as google

from .artifact import Artifact

class Archive:
    """An archive to push artifacts into
    """

    def collect(self, artifact: Artifact, outputName: str) -> bool:
        """Pushes an artifact into this archive

        :param self:
            Self
        :param artifact:
            The artifact to collect
        :param outputName:
            The name of the artifact when archived

        :return True:
            Artifact collected
        :return False:
            Failed to collect artifact
        """

        raise NotImplementedError("It belongs in a museum!")

    def __str__(self) -> str:
        """Creates a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        raise NotImplementedError("No string-er for archive")

class DirectoryArchive(Archive):
    """A local archive directory
    """

    def __init__(self, directory: str) -> None:
        """Creates a new directory archive

        :param self:
            Self
        :param directory:
            The directory to collect artifacts in

        :return none:
        """

        self._directory = directory

    def __str__(self) -> str:
        """Creates a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        return self._directory

    def collect(self, artifact: Artifact, outputName: str) -> bool:
        """Collects an artifact for the archive

        :param self:
            Self
        :param artifact:
            The artifact to collect

        :return True:
            Artifacts collected
        :return False:
            Failed to collect artifacts
        """

        # Get the full destination path for the artifact
        outputPath = os.path.join(self._directory, outputName)

        # Make sure our destination directories exist
        os.makedirs(os.path.dirname(outputPath), exist_ok = True)

        # Copy the file over to its destination
        shutil.copyfile(src = artifact.fileName, dst = outputPath)

        return True

class CloudArchive(Archive):
    """A cloud storage archive
    """

    def __init__(self, directory: str, storage: google.Storage) -> None:
        """Creates a new cloud storage archive

        :param self:
            Self
        :param directory:
            The output cloud storage directory
        :param storage:
            The storage to push to

        :return none:
        """

        self._directory = directory
        self._storage = storage

    def collect(self) -> bool:
        """Collects artifacts for the archive

        :param self:
            Self

        :return True:
            Artifacts collected
        :return False:
            Failed to collect artifacts
        """

        pass
