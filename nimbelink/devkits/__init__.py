"""
The NimbeLink devkit package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

__all__ = [
    "Host",
]
# Conditional imports
try:
    from nimbelink.devkits.NLSWN_RPI import NLSWN_RPI
    __all__.append("NLSWN_RPI")
except ModuleNotFoundError:
    # Raspberry Pi Host unavailable
    pass
