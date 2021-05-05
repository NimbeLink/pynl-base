"""
A command-line user menu

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing
import sys

class Menu:
    """A command-line user menu
    """

    def __init__(self, prompt: str, items: typing.List[object], currentValue: object = None):
        """Creates a new menu

        :param self:
            Self
        :param prompt:
            The prompt text explaining the selection choice(s)
        :param items:
            The selection choices
        :param currentValue:
            The current value, if any

        :return none:
        """

        self._prompt = prompt
        self._items = items
        self._currentValue = currentValue

    def getSelection(self):
        """Gets a selection for our menu

        :param self:
            Self

        :return None:
            Menu exited
        :return object:
            The selection from the item list
        """

        while True:
            sys.stdout.write("{}:\n".format(self._prompt))

            for i in range(len(self._items)):
                sys.stdout.write("{:4d}: {}".format(i + 1, self._items[i]))

                if self._items[i] == self._currentValue:
                    sys.stdout.write(" (current)")

                sys.stdout.write("\n")

            sys.stdout.write("\n")
            sys.stdout.write("Enter selection: ")
            sys.stdout.flush()

            input = sys.stdin.readline().rstrip()

            sys.stdout.write("\n")

            if len(input) < 1:
                if self._currentValue != None:
                    return self._currentValue

                sys.stdout.write("Please enter a selection\n")
                continue

            try:
                selection = int(input)

            except ValueError:
                sys.stdout.write("Please enter a valid number ({})\n".format(input))
                continue

            if selection > len(self._items):
                sys.stdout.write("Invalid selection {}\n".format(selection))
                continue

            break

        return self._items[selection - 1]
