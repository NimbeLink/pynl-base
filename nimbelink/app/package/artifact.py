"""
Application artifacts

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import os

class Artifact:
    """A local artifact of interest
    """

    def __init__(self, fileName: str):
        """Creates a new artifact

        :param self:
            Self
        :param fileName:
            The file to collect

        :return none:
        """

        self.fileName = fileName

    def __str__(self) -> str:
        """Creates a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        return self.fileName

    @property
    def name(self) -> str:
        """Gets our base name

        :param self:
            Self

        :return str:
            Our name
        """

        return os.path.basename(self.fileName)

    @property
    def directory(self) -> str:
        """Gets our containing directory

        :param self:
            Self

        :return str:
            Our directory
        """

        return os.path.dirname(self.fileName)
