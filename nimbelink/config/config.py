###
 # \file
 #
 # \brief Configuration with file-based storage
 #
 #  This module defines the Option and Config class. These classes work together
 #  to produce a structure similar to a Unix directory tree containing Configs.
 #
 # (C) NimbeLink Corp. 2021
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

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

    def __init__(self, name: str, valueType = None, value = None):
        """Creates a new configuration option

        :param self:
            Self
        :param name:
            The name of this option
            :param valueType:
                The type of value this contains
        :param value:
            The value of this option

        :return none:
        """

        # If the value type wasn't specified
        if valueType == None:
            # If the value was specified, fill in the type with it
            if value != None:
                valueType = type(value)

            # Else, default to something easy
            else:
                valueType = object

        self._name = name
        self._valueType = valueType
        self._value = value

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
    def valueType(self):
        """Get the value type of an option

        :param self:
            Self

        :return object:
            The value type of the option
        """

        return self._valueType

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

        if isinstance(newValue, self._valueType):
            self._value = newValue
            return

        try:
            self._value = self._valueType(newValue)

        except ValueError:
            raise TypeError("Invalid type {} for option '{}' of type {}".format(type(newValue), self._name, self._valueType))

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
        """Find an option in this level or levels above and return its current
        value

        :param self:
            Self
        :param name:
            The option name to get the value for

        :raise KeyError:
            Option not found in config

        :return object:
            The Option or Config named name
        """

        # Search in this config first for the option
        for option in self._options:
            if option.name == name:
                return option.value

        # Next try to see if this is a sub-configuration of ours
        for subConfig in self._subConfigs:
            if subConfig.name == name:
                return subConfig

        # Option not found in config
        raise KeyError("Unable to find \"{}\" in Config".format(name))

    def __setitem__(self, name: str, newValue):
        """Find an option in this level or levels above and set its current
        value

        :param self:
            Self
        :param name:
            The name of the Option to set
        :param newValue:
            The value to set the Option to

        :raise KeyError:
            Option not found in config

        :return none:
        """

        # Search in this config first for the option
        for option in self._options:
            if option.name == name:
                option.value = newValue
                return

        # Option not found in config
        raise KeyError("Unable to find \"{}\" in Config".format(name))

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
    def _getDictEntries(config: "Config"):
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
            data[subConfig.name] = Config._getDictEntries(config = subConfig)

        return data

    @staticmethod
    def _makeFromDict(name: str, data: dict):
        """Makes a configuration from a dictionary

        :param name:
            The name of the configuration
        :param data:
            The dictionary data to parse

        :return Config:
            The config
        """

        config = Config(name = name)

        for key in data:
            # If this is a new configuration, add one for it and iterate over
            # its options and sub-configs
            if isinstance(data[key], dict):
                config.add(Config._makeFromDict(name = key, data = data[key]))

            # Else, this is an option, so add one for it
            else:
                config.add(Option(name = key, valueType = type(data[key]), value = data[key]))

        return config

    @staticmethod
    def saveToFile(config: "Config", filename: str = "config.yaml"):
        """Saves configuration values to a file

        :param config:
            The configuration to save
        :param filename:
            The file to save the configuration to

        :return none:
        """

        # Write the config to disk
        with open(filename, "w") as configFile:
            data = {
                config.name: Config._getDictEntries(config = config)
            }

            yaml.dump(data, configFile, Dumper = Dumper)

    @staticmethod
    def loadFromFile(filename: str = "config.yaml"):
        """Loads configuration values from a file

        :param filename:
            The file to load the configuration from

        :raise OSError:
            Failed to load configuration from file

        :return Config:
            The loaded configuration
        """

        # Try to open the previous config file
        try:
            with open(filename, "r") as configFile:
                # Read in existing configuration
                data = yaml.load(configFile, Loader = Loader)

        # If the file doesn't exist, use an empty configuration
        except FileNotFoundError:
            return Config()

        # If there wasn't any data, use an empty configuration
        if data == None:
            return Config()

        # If the data doesn't start with our famous 'root' entry, use an empty
        # configuration
        if "root" not in data:
            return Config()

        return Config._makeFromDict(name = "root", data = data["root"])
