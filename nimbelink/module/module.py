"""
An installable NimbeLink Python package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

class Module:
    """An installable NimbeLink Python package
    """

    Prefix = "nl_"
    """A prefix we expect all NimbeLink-provided packages to use"""

    @staticmethod
    def getAlias(name: str) -> str:
        """Finds a package name 'alias' for an installable Python package
        'module'

        :param name:
            The package name to find an alias for

        :raise ValueError:
            Failed to derive an alias for the package from its name

        :return str:
            The alias
        """

        # If the name doesn't start with our standard prefix, that's a paddlin'
        if not name.startswith(Module.Prefix):
            raise ValueError("Package name '{}' doesn't start with '{}'!".format(name, Module.Prefix))

        # Strip the prefix and call the rest the 'alias'
        return name[len(Module.Prefix):]

    def __init__(self, name: str, alias: str = None) -> None:
        """Creates a new module

        :param self:
            Self
        :param name:
            The name of the installable module
        :param alias:
            The local alias to use when linking it into the 'nimbelink' package

        :return none:
        """

        # If they didn't provide an alias, try to auto-derive one
        if alias == None:
            alias = Module.getAlias(name = name)

        self.name = name
        self.alias = alias
