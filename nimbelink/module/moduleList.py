"""
A list of NimbeLink modules

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

from .module import Module

class ModuleList:
    """A list of pynl packages

    Any modules from different packages that wish to be available under the
    'nimbelink' package namespace can register their instantiated
    nimbelink.modules.Module object to this list.
    """

    def __init__(self) -> None:
        """Creates a new module list

        :param self:
            Self

        :return none:
        """

        self.__modules = None

    def _cacheModules(self) -> None:
        """Caches our module list

        :param self:
            Self

        :return none:
        """

        import nimbelink.cache

        nimbelink.cache.getCache("modules").set("list", self.__modules)

    @property
    def _modules(self) -> typing.List:
        """Gets our registered modules, potentially fetching them from our cache

        :param self:
            Self

        :return none:
        """

        # If our modules have already been loaded, nothing to do
        if self.__modules is not None:
            return self.__modules

        # Set up our array
        self.__modules = []

        import nimbelink.cache

        # Try to get our modules
        registeredModules = nimbelink.cache.getCache("modules").get("list")

        # If that failed, nothing to load
        if registeredModules is None:
            return self.__modules

        # Grab all of our modules
        #
        # Note that we'll iterate through the returned list and manually append
        # them, as reassigning the __modules__ list itself to the returned list
        # does not appear to behave correctly... Actually not sure what's going
        # on there.
        for registeredModule in registeredModules:
            # Make sure any duplicates are dropped
            if registeredModule.name in [module.name for module in self.__modules]:
                continue

            self.__modules.append(registeredModule)

        # If we filtered out any duplicates, recache our module list
        if len(self.__modules) != len(registeredModules):
            self._cacheModules()

        # Prune our list of modules that are no longer available
        self.prune()

        return self.__modules

    def __str__(self) -> str:
        """Gets a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        return str(self._modules)

    def __repr__(self) -> str:
        """Gets a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        return repr(self._modules)

    def __getitem__(self, key: int) -> Module:
        """Gets a module from the list

        :param self:
            Self
        :param key:
            The module to get

        :return Module:
            The module
        """

        return self._modules[key]

    def __iter__(self) -> None:
        """Gets modules from our list

        :param self:
            Self

        :yield Module:
            The next module in our list

        :return none:
        """

        for module in self._modules:
            yield module

    def append(self, module: Module) -> None:
        """Appends a new module

        :param self:
            Self
        :param module:
            The module to append

        :return none:
        """

        # If this module is already registered, nothing to do
        if module in self._modules:
            return

        self._modules.append(module)

        # We've got a new module, so re-cache our new list
        self._cacheModules()

    def remove(self, module: Module) -> None:
        """Removes a module

        :param self:
            Self
        :param module:
            The module to remove

        :return none:
        """

        # Note our starting length
        startLength = len(self._modules)

        # Try to remove the module
        self._modules.remove(module)

        # If we actually removed a module, re-cache our new list
        if len(self._modules) != startLength:
            self._cacheModules()

    def prune(self) -> None:
        """Prunes modules that no longer exist

        :param self:
            Self

        :return none:
        """

        # Note our starting length
        startLength = len(self._modules)

        i = 0

        while True:
            # If we're out of modules to examine, move on
            if i >= len(self._modules):
                break

            # If this module doesn't exist, remove it
            if not self._modules[i].exists():
                self._modules.pop(i)

            # Else, move on to the next module
            else:
                i += 1

        # If we actually removed modules, re-cache our new list
        if len(self._modules) != startLength:
            self._cacheModules()
