"""
A command that can be run from the command line or using Python specifically

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from .command import Command

__all__ = [
    "Command",
]

__commands__ = [
]
"""Commands that are available for running from the command-line

Any modules that wish to have their modules registered for running from the
command-line can register their instantiated nimbelink.command.Command object to
this list. Each command's name will be registered as a sub-command under the
top-level 'nimbelink' module's command.
"""

def register(command: Command) -> None:
    """Registers a new sub-command

    :param command:
        The command to register

    :return none:
    """

    __commands__.append(command)
