"""
NimbeLink modules

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from .command import ModuleCommand
from .module import Module

__all__ = [
    "Module",

    "ModuleCommand",
]

import nimbelink.command as command

command.register(command = ModuleCommand())

__modules__ = [
]
"""Dynamic 'nimbelink' submodules

Any modules from different packages that wish to be available under the
'nimbelink' package namespace can register their instantiated
nimbelink.modules.Module object to this list.
"""

import diskcache
import os

def __getCache() -> diskcache.Cache:
    """Gets our local diskcache

    :param none:

    :return diskcache.Cache:
        Our cache
    """

    # Get this script's directory and use its local __pycache__ to store the
    # file(s)
    return diskcache.Cache(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "__pycache__"
    ))

def __loadModules() -> None:
    """Loads our registered modules from our cache

    :param none:

    :return none:
    """

    # Try to get our modules
    registeredModules = __getCache().get(key = "modules")

    # If that worked, make them live
    #
    # Note that we'll iterate through the returned list and manually append
    # them, as reassigning the __modules__ list itself to the returned list does
    # not appear to behave correctly... Actually not sure what's going on there.
    if registeredModules != None:
        for registeredModule in registeredModules:
            __modules__.append(registeredModule)

def register(module: Module) -> None:
    """Registers a new submodule

    :param module:
        The module to register

    :return none:
    """

    # If this module is already registered, nothing to do
    if module in __modules__:
        return

    # Append this to our 'live' modules
    __modules__.append(module)

    # Cache our new list of modules
    __getCache().set(key = "modules", value = __modules__)

def unregister(module: Module) -> None:
    """Unregisters a submodule

    :param module:
        The module to unregister

    :return none:
    """

    for i in range(len(__modules__)):
        if module == __modules__[i]:
            # Remove this from our 'live' modules
            __modules__.pop(i)

            # Cache our new list of modules
            __getCache().set(key = "modules", value = __modules__)

__loadModules()
