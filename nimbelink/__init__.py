"""
The NimbeLink package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

__all__ = [
    "app",
    "cloud",
    "config",
    "debugger",
    "git",
    "module",
    "ui",
    "utils"
]

import importlib
import sys

class PynlFinder(importlib.abc.MetaPathFinder):
    """A submodule finder for loading dynamic NimbeLink modules
    """

    def find_spec(self, fullname, path, target = None):
        """Finds pynl-like submodule specs

        :param self:
            Self
        :param fullname:
            The name of the package to try to find
        :param path:
            The path being sought
        :param target:
            The target

        :return None:
            Failed to find module
        """

        packages = fullname.split(".")

        # If they aren't looking for a 'nimbelink'-scoped package, this must not
        # be for a pynl package
        if packages[0] != "nimbelink":
            return None

        # If this isn't for a first-level pynl package, we won't be able to load
        # whatever this is for them
        #
        # In this case, we likely loaded the pynl package but now the user is
        # trying to access something within the (loaded) package that doesn't
        # exist.
        if len(packages) != 2:
            return None

        import nimbelink.module

        # Clean up any dangling modules that no longer exist
        nimbelink.module.__modules__.prune()

        for module in nimbelink.module.__modules__:
            # If this is the module they're trying to find, great, found it
            if module.alias == packages[1]:
                return module.doImport()

        return None

# Add our submodule finder to the system
sys.meta_path.append(PynlFinder())
