"""
Git versioning

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from .base import Base
from .info import Info

from .version import Version

__all__ = [
    "Base",
    "Info",
    "Version",
]

import nimbelink.command as command
from .__cmd__ import VersionCommand

command.register(command = VersionCommand())