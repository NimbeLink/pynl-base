"""
The NimbeLink modem package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from .config import Config
from .option import Option

from .backend import Backend
from .yaml import YamlBackend

__all__ = [
    "Config",
    "Option",

    "Backend",
    "YamlBackend",
]

# The West backend is only available if the local system has the 'west' package
# installed, which we don't require
try:
    from .west import WestBackend
    __all__.append("WestBackend")
except ImportError:
    pass
