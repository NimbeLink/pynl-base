"""
NimbeLink modules

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import diskcache
import os

from .module import Module

__all__ = [
    "Module",

    "register",
    "unregister"
]

import nimbelink.command as command
from .__cmd__ import ModuleCommand

command.register(command = ModuleCommand())

__modules__ = [
]
"""Dynamic 'nimbelink' submodules

Any modules from different packages that wish to be available under the
'nimbelink' package namespace can register their instantiated
nimbelink.modules.Module object to this list.
"""

def __getCache() -> diskcache.Cache:
    """Gets our local diskcache

    :param none:

    :return None:
        Failed to get our cache
    :return diskcache.Cache:
        Our cache
    """

    # Get this script's directory and use its local __pycache__ to store the
    # file(s)
    try:
        return diskcache.Cache(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "__pycache__"
        ))

    except Exception:
        return None

def __cacheModules() -> None:
    """Caches our module list

    :param none:

    :return none:
    """

    cache = __getCache()

    if cache is None:
        return

    cache.set(key = "modules", value = __modules__)

def __loadModules() -> None:
    """Loads our registered modules from our cache

    :param none:

    :return none:
    """

    cache = __getCache()

    if cache is None:
        return

    # Try to get our modules
    registeredModules = cache.get(key = "modules")

    # If that failed, nothing to load
    if registeredModules is None:
        return

    # Clear any existing modules
    __modules__.clear()

    # Grab all of our modules
    #
    # Note that we'll iterate through the returned list and manually append
    # them, as reassigning the __modules__ list itself to the returned list does
    # not appear to behave correctly... Actually not sure what's going on there.
    for registeredModule in registeredModules:
        # Make sure any duplicates are dropped
        if registeredModule.name in [module.name for module in __modules__]:
            continue

        __modules__.append(registeredModule)

    # If we filtered out any duplicates, recache our module list
    if len(__modules__) != len(registeredModules):
        __cacheModules()

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

    # Update our cache
    __cacheModules()

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

            # Update our cache
            __cacheModules()

            break

__loadModules()
