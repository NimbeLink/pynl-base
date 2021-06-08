"""
Configuration with file-based storage

This module defines the Option and Config class. These classes work together to
produce a structure similar to a Unix directory tree containing Configs.

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing
import yaml

try:
    # Try to use the libyaml bindings
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper

except ImportError:
    # Fall back to pure python yaml library
    from yaml import Loader
    from yaml import Dumper

class Option():
    """This class represents a configuration option

    Usually an option's value is not set on Option creation and is set from the
    Config class using the .value = <value> notation. The value of the object
    can be retrieved with the value property.

    Example:

        # Somewhere in initialization
        option = Option("my_option")
        config.add_option(option)

        # config sets option's value

        # Somewhere in initialization
        option = Option("my_option")
        config.add_option(option)

        # Somewhere in program main run
        print(option.value)
    """

    @staticmethod
    def toBool(value):
        """Converts a value to a boolean

        :param value:
            The value to convert

        :raise TypeError:
            Invalid boolean-like value

        :return True:
            True
        :return False:
            False
        """

        if isinstance(value, bool):
            return value

        if value.lower() in ["yes", "y", "true", "t", "1"]:
            return True

        if value.lower() in ["no", "n", "false", "f", "0"]:
            return False

        raise TypeError("Failed to convert '{}' to a boolean".format(value))

    def __init__(
        self,
        name: str,
        type: object = None,
        value: object = None,
        choices: typing.List[object] = None
    ):
        """Creates a new configuration option

        :param self:
            Self
        :param name:
            The name of this option
        :param type:
            The type of value this contains
        :param value:
            The value of this option
        :param choices:
            The available values to choose from

        :return none:
        """

        self._name = name
        self._type = type
        self._value = value
        self._choices = choices

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
    def type(self):
        """Get the value type of an option

        :param self:
            Self

        :return object:
            The value type of the option
        """

        if self._value != None:
            return type(self._value)

        return self._type

    @property
    def choices(self):
        """Gets the available values to choose from

        :param self:
            Self

        :return List[object]:
            The available choices
        """

        return self._choices

    @property
    def value(self):
        """Get the value of an option

        :param self:
            Self

        :return object:
            The value of the option or None
        """

        return self._value

    @value.setter
    def value(self, newValue):
        """Set the value of an option

        This is usually used with in the Config class

        :param self:
            Self
        :param newValue:
            The value to set the option to

        :return none:
        """

        if self._choices != None:
            if newValue not in self._choices:
                raise TypeError("Invalid value {} for choices {}".format(newValue, self._choices))

        if isinstance(newValue, self._type):
            self._value = newValue
            return

        try:
            self._value = self._type(newValue)

        except ValueError:
            raise TypeError("Invalid type {} for option '{}' of type {}".format(type(newValue), self._name, self._type))

    def __str__(self):
        """Get a string representation of the option

        :param self:
            Self

        :return String:
            Us as a string
        """

        string = "{}:".format(self._name)

        if self._value != None:
            string += " {}".format(self._value)

        return string

class Config():
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

        self.name = name

        self._subConfigs = []
        self._options = []

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

    def add(self, thing: typing.Union[Option, "Config"]):
        """Add an option or sub-config to this level of configuration

        :param self:
            Self
        :param thing:
            The option or sub-config to add to this level of configuration

        :raise ValueError:
            Thing cannot be added to config

        :return Option:
            The added option
        """

        try:
            name = thing.name

            bad = self[name]

            raise ValueError("{} '{}' already exists".format(type(thing), thing.name))

        except (KeyError, AttributeError) as ex:
            pass

        if isinstance(thing, Option):
            self._options.append(thing)

        elif isinstance(thing, Config):
            self._subConfigs.append(thing)

        else:
            raise ValueError("Can't add {} to config".format(type(thing)))

        return thing

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

        raise KeyError("Unable to find \"{}\" in Config".format(name))

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

        raise KeyError("Unable to find \"{}\" in Config".format(name))

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

        raise KeyError("Unable to find \"{}\" in Config".format(name))

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

        string = "config {}:".format(self.name)

        for option in self._options:
            string += "\n    option {}".format(option)

        for subConfig in self._subConfigs:
            subConfigString = "{}".format(subConfig)

            for line in subConfigString.split("\n"):
                string += "\n    {}".format(line)

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

    @staticmethod
    def _getConfigDict(config: "Config"):
        """Gets a dictionary entry from a config

        :param config:
            The configuration whose entry to get

        :return Dictionary:
            The config's entries
        """

        data = {}

        for option in config.options:
            data[option.name] = option.value

        for subConfig in config.subConfigs:
            data[subConfig.name] = Config._getConfigDict(config = subConfig)

        return data

    @staticmethod
    def _getFileDict(filename: str):
        """Gets a file's dictionary of data

        :param filename:
            The file to get a dictionary from

        :raise OSError:
            Failed to get dictionary from file

        :return dict:
            The dictionary of data
        """

        # Try to open the previous config file
        try:
            with open(filename, "r") as configFile:
                # Read in existing configuration
                data = yaml.load(configFile, Loader = Loader)

        # If the file doesn't exist, use an empty configuration
        except FileNotFoundError:
            raise OSError("Failed to load file {}".format(filename))

        # If there wasn't any data, use an empty configuration
        if data == None:
            raise OSError("No data found in file {}".format(filename))

        # If the data doesn't start with our famous 'root' entry, use an empty
        # configuration
        if "root" not in data:
            raise OSError("No 'root' configuration found in file {}".format(filename))

        return data

    @staticmethod
    def _makeFromDict(name: str, data: dict):
        """Makes a configuration from a dictionary

        :param name:
            The name of the configuration
        :param data:
            The configuration's data

        :return Config:
            The configuration
        """

        config = Config(name = name)

        for key in data:
            # If this is a new configuration, add one for it and iterate over
            # its options and sub-configs
            if isinstance(data[key], dict):
                config.add(Config._makeFromDict(name = key, data = data[key]))

            # Else, this is an option, so add one for it
            else:
                config.add(Option(name = key, type = type(data[key]), value = data[key]))

        return config

    @staticmethod
    def _loadFromDict(config: "Config", data: dict):
        """Loads a configuration from a dictionary

        :param config:
            The configuration to load
        :param data:
            The configuration's data

        :raise OSError:
            Failed to load configuration from dictionary

        :return none:
        """

        for key in data:
            # If this isn't found in our items, that's a paddlin'
            if key not in config:
                raise OSError("Item {} not found in config".format(key))

            # If the item is a configuration but our item isn't; or vice versa,
            # that's a paddlin'
            if isinstance(data[key], dict):
                if not isinstance(config[key], Config):
                    raise OSError("Item {} is a Config but should be an Option".format(key))

                Config._loadFromDict(config = config[key], data = data[key])

            else:
                if not isinstance(config[key], Option):
                    raise OSError("Item {} is an Option but should be a Config".format(key))

                config[key] = data[key]

    def saveToFile(self, filename: str = "config.yaml"):
        """Saves configuration values to a file

        :param self:
            Self
        :param filename:
            The file to save the configuration to

        :return none:
        """

        # Write the config to disk
        with open(filename, "w") as configFile:
            data = {
                self.name: Config._getConfigDict(config = self)
            }

            yaml.dump(data, configFile, Dumper = Dumper)

    def loadFromFile(self, filename: str = "config.yaml"):
        """Loads a configuration from a file

        :param self:
            Self
        :param filename:
            The file to load the configuration from

        :raise OSError:
            Failed to load configuration from file

        :return none:
        """

        return self._loadFromDict(
            data = Config._getFileDict(filename = filename)["root"]
        )

    @staticmethod
    def makeFromFile(filename: str = "config.yaml"):
        """Makes a configuration from a file

        :param filename:
            The file to load the configuration from

        :raise OSError:
            Failed to load configuration from file

        :return Config:
            The loaded configuration
        """

        return Config._makeFromDict(
            name = "root",
            data = Config._getFileDict(filename = filename)["root"]
        )