"""
The root NimbeLink command

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

from .command import Command

class RootCommand(Command):
    """Our root command
    """

    def __init__(self, subCommands: typing.List[Command]) -> None:
        """Creates a new root command

        :param self:
            Self
        :param subCommands:
            Our sub-commands

        :return none:
        """

        super().__init__(
            name = "root",
            help = "provides sub-commands",
            subCommands = subCommands
        )
