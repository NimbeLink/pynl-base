"""
A command-line user entry

(C) NimbeLink Corp. 2021

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

    def __init__(self, prompt: str, currentValue: object = None):
        """Creates a new entry

        :param self:
            Self
        :param prompt:
            The prompt text explaining the entry
        :param currentValue:
            The current value, if any

        :return none:
        """

        self._prompt = prompt
        self._currentValue = currentValue

    def getInput(self):
        """Gets input for our entry

        :param self:
            Self

        :return None:
            Entry exited
        :return String:
            The free-form entry
        """

        while True:
            sys.stdout.write(f"{self._prompt}")

            if self._currentValue != None:
                sys.stdout.write(" (current ")

                if isinstance(self._currentValue, str):
                    sys.stdout.write("'")

                sys.stdout.write(f"{self._currentValue}")

                if isinstance(self._currentValue, str):
                    sys.stdout.write("'")

                sys.stdout.write(")")

            sys.stdout.write(": ")
            sys.stdout.flush()

            input = sys.stdin.readline().rstrip()

            sys.stdout.write("\n")

            if len(input) < 1:
                if self._currentValue != None:
                    return self._currentValue

                sys.stdout.write("Please enter a value\n")
                continue

            break

        return input
