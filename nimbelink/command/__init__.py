"""
A command that can be run from the command line or using Python specifically

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

from .command import Command
from .wsl import Wsl

__all__ = [
    "Command",
    "Wsl",

    "register",
    "run"
]

# West commands are only available if the local system has the 'west' package
# installed, which we don't require
try:
    from .westCommand import WestCommand
    __all__.append("WestCommand")
except ImportError:
    pass

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

    # If we've already got a command like this, ignore it
    if command._name in [existingCommand._name for existingCommand in __commands__]:
        return

    __commands__.append(command)

def run(args: typing.List[object] = None) -> int:
    """Runs our commands with arguments

    If arguments are not provided, sys.argv will be automatically used.

    :param args:
        The arguments to run with

    :return int:
        The result of the command
    """

    return Command(
        name = "nimbelink",
        help = "Provides sub-commands",
        subCommands = __commands__
    ).parseAndRun(args = args)
