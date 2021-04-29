###
 # \file
 #
 # \brief A command-line user menu
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import typing
import sys

class Menu:
    """A command-line user menu
    """

    def __init__(self, prompt: str, items: typing.List[object]):
        """Creates a new menu

        :param self:
            Self
        :param prompt:
            The prompt text explaining the selection choice(s)
        :param items:
            The selection choices

        :return none:
        """

        # Make sure we can dress up the text as we like without duplicating
        # things provided
        prompt = prompt.rstrip().rstrip(":")

        self._prompt = prompt
        self._items = items

    def getSelection(self):
        """Gets a selection for our menu

        :param self:
            Self

        :return None:
            Menu exited
        :return object:
            The selection from the item list
        """

        sys.stdout.write("{}:\n".format(self._prompt))

        for i in range(len(self._items)):
            sys.stdout.write("{:4d}: {}\n".format(i + 1, self._items[i]))

        sys.stdout.write("\n")
        sys.stdout.write("Enter selection: ")
        sys.stdout.flush()

        try:
            while True:
                input = sys.stdin.readline().rstrip()

                try:
                    selection = int(input)

                except ValueError:
                    sys.stdout.write("Please enter a valid number ({})".format(input))
                    continue

                if selection > len(self._items):
                    sys.stdout.write("Invalid selection {}".format(selection))
                    continue

                break

        except KeyboardInterrupt:
            return None

        return self._items[selection - 1]
