"""
A command-line user entry

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing
import sys

class Entry:
    """A command-line user entry
    """

    def __init__(self, prompt: str):
        """Creates a new entry

        :param self:
            Self
        :param prompt:
            The prompt text explaining the entry

        :return none:
        """

        # Make sure we can dress up the text as we like without duplicating
        # things provided
        prompt = prompt.rstrip().rstrip(":")

        self._prompt = prompt

    def getInput(self):
        """Gets input for our entry

        :param self:
            Self

        :return None:
            Entry exited
        :return String:
            The free-form entry
        """

        sys.stdout.write("{}: ".format(self._prompt))
        sys.stdout.flush()

        try:
            input = sys.stdin.readline().rstrip()

        except KeyboardInterrupt:
            return None

        return input
