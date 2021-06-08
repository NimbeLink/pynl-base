"""
The NimbeLink package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from . import cell
from . import command
from . import config
from . import devkits
from . import modules
from . import ui
from . import utils

__all__ = [
    "cell",
    "config",
    "devkits",
    "modules",
    "ui",
    "utils"
]

def __importModules():
    """Imports our dynamic NimbeLink modules

    :param none:

    :return none:
    """

    import importlib
    import os

    import nimbelink.modules as modules

    for module in modules.KnownModules:
        try:
            # Try to import the module that may or may not be locally available
            importedModule = importlib.import_module(name = module.name)

            # That worked, so add its root directory to our submodule search
            # path so it can be looked up as if under our 'nimbelink' root
            # package
            globals()["__spec__"].submodule_search_locations.append(
                os.path.dirname(importedModule.__file__)
            )

            # Make sure our 'all' looks like it contains this now-look-up-able
            # module
            __all__.append(module.alias)

        except ImportError as ex:
            pass

__importModules()
