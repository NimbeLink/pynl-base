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
import importlib.metadata
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

Any modules that wish to have their commands registered for running from the
command-line can include 'entry_points' entries in their package that configure
first-level sub-commands to link into the root command. The 'name' field is
ignored by the command handling. The 'value' field should point to the file and
command to be included. For example, in a setup.cfg:

    [options.entry_points]
    pynl.commands =
        myentry = my.package.command:MyCommand

The commands used should not take any parameters for instantiation.
"""

def register(command: Command) -> None:
    """Registers a new sub-command

    :param command:
        The command to register

    :return none:
    """

    __commands__.append(command)

def _discoverCommands(entryPointsName: str) -> None:
    """Discovers registered pynl commands

    :param entryPointsName:
        The entry points to discover sub-commands for

    :return none:
    """

    # Add the 'commands' component to the entry points namespace
    #
    # This forms the:
    #
    #   [options.entry_points]
    #   <entryPointsName>.commands =
    #
    # component of the Python package options.
    entryPointsName += ".commands"

    # Get the Python entry points
    entryPoints = importlib.metadata.entry_points()

    # If our pynl commands entry doesn't exist, we must not have any entry
    # points registered
    if entryPointsName not in entryPoints:
        return

    for commandEntryPoint in entryPoints[entryPointsName]:
        # Get the file and command from the 'value', which are separated by a
        # ':'
        fields = commandEntryPoint.value.split(":")

        # If this entry wasn't properly formatted, skip it
        if len(fields) != 2:
            continue

        # Import the module
        module = importlib.import_module(fields[0])

        # If the module doesn't have the specified class, skip it
        if not hasattr(module, fields[1]):
            continue

        # Get the command
        command = getattr(module, fields[1])

        # Be paranoid and double-check that we got the class
        if command is None:
            continue

        # Register the discovered command
        register(command = command)

def run(args: typing.List[object] = None, entryPointsName: str = None) -> int:
    """Runs our commands with arguments

    If arguments are not provided, sys.argv will be automatically used.

    :param args:
        The arguments to run with
    :param entryPointsName:
        The entry points namespace to find sub-commands in

    :return int:
        The result of the command
    """

    if entryPointsName is None:
        entryPointsName = "pynl"

    _discoverCommands(entryPointsName = entryPointsName)

    return Command(
        name = "nimbelink",
        help = "Provides sub-commands",
        subCommands = __commands__
    ).parseAndRun(args = args)
