"""
A command that can be run from the command line or using Python specifically

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import importlib
import os
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
command-line can include a __cmd__.py file in their nimbelink.<path> submodule
directory, which should contain a __commands__ array of commands. The commands
can be either classes or instantiated objects, but should *not* be string names
of classes (i.e. they need to be a reference to an imported class or an
instantiated object).

When commands are run, all discovered commands will be linked into the top-level
list as direct sub-commands.
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

    # Get our 'nimbelink' namespace spec
    spec = importlib.util.find_spec("nimbelink")

    # In each submodule search location, try to find potential submodules with
    # sub-commands
    for location in spec.submodule_search_locations:
        for submoduleName in os.listdir(location):
            fullPath = os.path.join(location, submoduleName)

            # If this isn't a directory, then it isn't a submodule
            if not os.path.isdir(fullPath):
                continue

            # If this directory doesn't contain a __cmd__.py file, then it might
            # be a submodule, but it doesn't have any commands it wishes to
            # register
            if not os.path.exists(os.path.join(fullPath, "__cmd__.py")):
                continue

            name = f"nimbelink.{submoduleName}.__cmd__"

            # Import the submodule that (should) contain the sub-command list
            module = importlib.import_module(name)

            # Double-check that they properly listed their commands
            if not hasattr(module, "__commands__"):
                continue

            # Double-check that they properly *listed* their commands
            if not isinstance(module.__commands__, list):
                continue

            # Add the submodule's commands to our sub-command list
            for command in module.__commands__:
                register(command = command)

    return Command(
        name = "nimbelink",
        help = "Provides sub-commands",
        subCommands = __commands__
    ).parseAndRun(args = args)
