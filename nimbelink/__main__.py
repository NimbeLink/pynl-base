"""
The main entry point for the NimbeLink package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import sys

import nimbelink.command as command
import nimbelink.modules as modules

class NlCommand(command.Command):
    """Our root NimbeLink command
    """

    def __init__(self):
        """Creates a new NimbeLink command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "nl-base",
            help = "provides NimbeLink Python package functionality",
            description =
                """Handles NimbeLink Python packages
                """,
            subCommands = [
                modules.ModuleCommand()
            ]
        )

    def addArguments(self, parser):
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        pass

def main():
    """Handles commands

    :param none:

    :return none:
    """

    nl = NlCommand()

    nl._parseAndRun()

if __name__ == "__main__":
    main()
