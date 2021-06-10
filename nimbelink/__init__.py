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

__addons__ = [
]
"""Additional submodules that are dynamically loaded from the local
environment"""

def __importModules():
    """Imports our dynamic NimbeLink modules

    :param none:

    :return none:
    """

    import importlib
    import sys

    import nimbelink.modules as modules

    for module in modules.KnownModules:
        try:
            # Try to import the module that may or may not be locally available
            importedModule = importlib.import_module(name = module.name)

            # That worked, so add it as a module under our namespace
            #
            # This allows someone to import 'nimbelink.x'.
            sys.modules["nimbelink." + module.alias] = importedModule

            # Make sure the module can be accessed directly without needing to
            # import it 'from' us
            #
            # This allows someone to access 'nimbelink.x' verbosely without
            # needing to 'import from' or 'import as'.
            #
            # With the preceding operation, someone can 'import nimbelink.x',
            # but until this operation they wouldn't be able to then use the
            # submodule. Something like 'help(nimbelink.x)' would actually fail,
            # despite the initial import working.
            globals()[module.alias] = importedModule

            # The above operations make the submodule fully usable by code that
            # knows about it, but it won't show up under the 'nimbelink' help
            # information, despite being namespaced. So, add it to a tracker
            # we'll use to show the available submodules we've dynamically
            # imported.
            __addons__.append(module.alias)

        except ImportError as ex:
            pass

__importModules()
