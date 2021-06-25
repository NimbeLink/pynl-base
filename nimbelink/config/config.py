"""
A dictionary-like configuration

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import functools
import typing

from .backend import Backend
from .option import Option

@functools.total_ordering
class Config:
    """This class creates a configuration container for different levels in the
    tests

    This class has a similar idea as a Unix directory structure. Each config has
    a list of Options and a list of sub-Configs.
    """

    def __init__(self, name: str = "root"):
        """Creates a new configuration

        :param self:
            Self
        :param name:
            The name of the Config level

        :return none:
        """

        self._name = name

        self._subConfigs = []
        self._options = []

        self._backend = None

    @property
    def name(self):
        """Get the name of an option

        :param self:
            Self

        :return String:
            The name of the option
        """

        return self._name

    @property
    def subConfigs(self):
        """Gets our sub-configurations

        :param self:
            Self

        :return Array of Config:
            Our configurations
        """

        return self._subConfigs

    @property
    def options(self):
        """Gets our options

        :param self:
            Self

        :return Array of Option:
            Our options
        """

        return self._options

    def clear(self) -> None:
        """Clears our sub-configurations and options

        :param self:
            Self

        :return none:
        """

        self._subConfigs = []
        self._options = []

    def add(self, thing: typing.Union[Option, "Config", Backend]):
        """Add something to this configuration

        :param self:
            Self
        :param thing:
            The thing to add to this configuration

        :raise ValueError:
            Thing cannot be added to configuration

        :return object:
            The added thing
        """

        if hasattr(thing, "name") and (thing.name in self):
            raise ValueError(f"{type(thing)} '{thing.name}' already exists")

        if isinstance(thing, Option):
            self._options.append(thing)

        elif isinstance(thing, Config):
            self._subConfigs.append(thing)

        elif isinstance(thing, Backend):
            self._backend = thing

        else:
            raise ValueError(f"Can't add {type(thing)} to config")

        return thing

    def __lt__(self, other: "Config") -> bool:
        """Checks if we're less than another configuration

        The comparison is done by comparing our name to theirs, meaning any
        sorting of configurations will result in an alphabetized list.

        :param self:
            Self
        :param other:
            The thing to compare us to

        :return True:
            We are 'less' than them
        :return False:
            We are 'greater than or equal' to them
        """

        return self._name < other._name

    def __len__(self) -> int:
        """Gets the number of options in our full configuration tree

        :param self:
            Self

        :return int:
            The number of options
        """

        count = len(self._options)

        for subConfig in self._subConfigs:
            count += len(subConfig)

        return count

    def __getitem__(self, name: str):
        """Get an Option or Config

        :param self:
            Self
        :param name:
            The name of the Option or Config to get

        :raise KeyError:
            Option or Config not found

        :return object:
            The Option or Config
        """

        for option in self._options:
            if option.name == name:
                return option.value

        for subConfig in self._subConfigs:
            if subConfig.name == name:
                return subConfig

        raise KeyError(f"Unable to find \"{name}\" in Config")

    def __setitem__(self, name: str, newValue):
        """Set an Option

        :param self:
            Self
        :param name:
            The name of the Option to set
        :param newValue:
            The value to set the Option to

        :raise KeyError:
            Option not found

        :return none:
        """

        for option in self._options:
            if option.name == name:
                option.value = newValue
                return

        raise KeyError(f"Unable to find \"{name}\" in Config")

    def __delitem__(self, name: str):
        """Deletes an Option or Config

        :param self:
            Self
        :param name:
            The name of the Option or Config to delete

        :raise KeyError:
            Option or Config not found

        :return none:
        """

        for i in range(len(self._options)):
            if self._options[i].name == name:
                del self._options[i]
                return

        for i in range(len(self._subConfigs)):
            if self._subConfigs[i].name == name:
                del self._subConfigs[i]
                return

        raise KeyError(f"Unable to find \"{name}\" in Config")

    def __contains__(self, item):
        """Checks if the configuration contains an item

        :param self:
            Self
        :param item:
            The item to check for

        :return True:
            Configuration contains the item
        :return False:
            Configuration does not contain the item
        """

        for option in self._options:
            # Allow an object or name match
            if (item == option) or (item == option.name):
                return True

        for subConfig in self._subConfigs:
            # Allow an object or name match
            if (item == subConfig) or (item == subConfig.name):
                return True

        return False

    def __str__(self):
        """Convert the configuration to a string

        :param self:
            Self

        :return String:
            Us as a string
        """

        # If we have a backend and it has a formatter, use it
        if self._backend is not None:
            try:
                return self._backend.format(self._getDict())

            except NotImplementedError:
                pass

        # Put this together ourselves
        string = f"config {self._name}:"

        for option in self._options:
            string += f"\n    option {option}"

        for subConfig in self._subConfigs:
            subConfigString = f"{subConfig}"

            for line in subConfigString.split("\n"):
                string += f"\n    {line}"

        return string

    def __iter__(self):
        """Iterates over configuration options

        :param self:
            Self

        :yield Tuple of String and object:
            The next option or the next configuration

        :return none:
        """

        # Yield the options
        for option in self._options:
            yield option

        # Yield the sub configs
        for subConfig in self._subConfigs:
            yield subConfig

    def _getDict(self):
        """Gets a dictionary from our contents

        :param self:
            Self

        :return Dictionary:
            The config's entries
        """

        data = {}

        # Add all of our options as values under a new dictionary entry
        for option in self._options:
            data[option.name] = option.value

        # Recursively add our sub-configs as dictionaries under a new dictionary
        # entry
        for subConfig in self._subConfigs:
            data[subConfig.name] = subConfig._getDict()

        return data

    def _loadFromDict(self, data: dict, allowCreate: bool = False):
        """Loads a configuration from a dictionary

        :param self:
            Self
        :param data:
            The configuration's data
        :param allowCreate:
            Whether or not to allow creating configurations and options on the
            fly

        :raise OSError:
            Failed to load configuration from dictionary

        :return none:
        """

        for key in data:
            # If this isn't found in our items
            if key not in self:
                # If we can't create something for it, that's a paddlin'
                if not allowCreate:
                    raise OSError(f"Item {key} not found in config")

                # If this is a new configuration
                if isinstance(data[key], dict):
                    # Make the new configuration
                    subConfig = Config(name = key)

                    # Recursively load its values
                    subConfig._loadFromDict(data = data[key], allowCreate = allowCreate)

                    # Add it as one of our sub-configs
                    self.add(subConfig)

                # Else, this is an option
                else:
                    # Make the new option
                    self.add(Option(name = key, type = type(data[key]), value = data[key]))

            # Else, if their version of the item is a configuration
            elif isinstance(data[key], dict):
                # If our version isn't a configuration, that's a paddlin'
                if not isinstance(self[key], Config):
                    raise OSError(f"Item {key} is a Config but should be an Option")

                # Recursively load our sub-config with the contents
                self[key]._loadFromDict(data = data[key], allowCreate = allowCreate)

            # Else, their version of the item is an option
            else:
                # If our version isn't an option, that's a paddlin'
                if isinstance(self[key], Config):
                    raise OSError(f"Item {key} is an Option but should be a Config")

                # Load our option with the contents
                self[key] = data[key]

    def save(self) -> bool:
        """Saves configuration values to our backend

        :param self:
            Self

        :return True:
            Configuration saved to backend
        :return False:
            Backend not available
        """

        if self._backend is None:
            return False

        self._backend.setDict(data = {"root": self._getDict()})

        return True

    def load(self, allowCreate: bool = False) -> bool:
        """Loads configuration values from our backend

        :param self:
            Self
        :param allowCreate:
            Whether or not to allow creating configurations and options on the
            fly

        :return True:
            Configuration loaded from backend
        :return False:
            Backend not available
        """

        if self._backend is None:
            return False

        data = self._backend.getDict()

        if "root" not in data:
            return True

        self._loadFromDict(data = data["root"], allowCreate = allowCreate)

        return True
