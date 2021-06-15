"""
Application artifact actions

Because artifacts are not always going to the same place with the same names,
artifacts and their destinations are tied together using 'actions', which entail
an artifact -- the source -- and an archive -- the destination. The action is
performed, with an optional renaming operation, and create the archives.

    Artifact 1  -> Action 1 ->  Archive 1
                -> Action 2 ->  Archive 1
                -> Action 3 ->  Archive 2
                ...
    ...

Each archive is expected to understand its own responsibilities for performing
the actions necessary to archive the artifact. That is, actions themselves
contain no operations other than linking archives and artifacts via the latter's
collect() API.

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import re

from .artifact import Artifact
from .archive import Archive

class Action:
    """An archival action
    """

    class Rename:
        """A rule for renaming an artifact

        The rule will be applied to the artifact's full file name, including any
        path.
        """

        def __init__(self, newNamePattern: str, oldNamePattern: str = None) -> None:
            """Creates a new rename rule

            This essentially wraps a 're.sub()' invocation.

            :param self:
                Self
            :param newNamePattern:
                A replacement pattern for the new name
            :param oldNamePattern:
                A regular expression for the old name

            :return none:
            """

            self._newNamePattern = newNamePattern
            self._oldNamePattern = oldNamePattern

        def __str__(self) -> str:
            """Creates a string representation of us

            :param self:
                Self

            :return str:
                Us
            """

            return f"'{self._oldNamePattern}' -> '{self._newNamePattern}'"

        def apply(self, artifact: Artifact) -> str:
            """Gets an artifact's new name

            :param self:
                Self
            :param artifact:
                The artifact whose new name to get

            :return str:
                The artifact's new name
            """

            if self._oldNamePattern is not None:
                pattern = self._oldNamePattern
            else:
                pattern = artifact.fileName

            return re.sub(
                pattern = pattern,
                repl = self._newNamePattern,
                string = artifact.fileName
            )

    def __init__(self, artifact: Artifact, archive: Archive, rename: "Action.Rename" = None) -> None:
        """Creates a new archive action

        :param self:
            Self
        :param artifact:
            The artifact to collect
        :param archive:
            The archive to push the artifact into
        :param renames:
            A rule for renaming the artifact, if any

        :return none:
        """

        self._artifact = artifact
        self._archive = archive
        self._rename = rename

    def __str__(self) -> str:
        """Creates a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        string = f"{self._artifact} -> {self._archive}"

        if self._rename is not None:
            string += f" ({self._rename})"

        return string

    def run(self) -> bool:
        """Runs the action

        :param self:
            Self

        :return True:
            Artifacts collected
        :return False:
            Failed to collect artifacts
        """

        if self._rename is not None:
            outputName = self._rename.apply(artifact = self._artifact)

        else:
            outputName = self._artifact.fileName

        return self._archive.collect(artifact = self._artifact, outputName = outputName)
