"""
NimbeLink modules

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from .module import Module
from .moduleList import ModuleList

__all__ = [
    "Module",
    "ModuleList",

    "register",
    "unregister"
]

import nimbelink.command
from .__cmd__ import ModuleCommand

nimbelink.command.register(command = ModuleCommand())

__modules__ = ModuleList()
"""The pynl packages we know about"""

def register(module: Module) -> None:
    """Registers a new submodule

    :param module:
        The module to register

    :return none:
    """

    __modules__.append(module = module)

def unregister(module: Module) -> None:
    """Unregisters a submodule

    :param module:
        The module to unregister

    :return none:
    """

    __modules__.remove(module = module)
