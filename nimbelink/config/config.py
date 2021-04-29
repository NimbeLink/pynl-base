###
 # \file
 #
 # \brief A Skywire Nano target
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

        return "{}:{}".format(self._name, self._value)

class Config():
    """This class creates a configuration container for different levels in the
    tests

    This class has a similar idea as a Unix directory structure. Each config has
    a list of Options, a list of sub-Configs, and a pointer to a parent Config.
    """

    def __init__(self, name: str, parentConfig: "Config" = None):
        """Creates a new configuration

        :param self:
            Self
        :param name:
            The name of the Config level
        :param parentConfig:
            A reference to the parent configuration. This is used to add this
            Config to the tree of configs but also when an Option is requested
            that is not in this level of config, the parent configurations are
            asked if they have that Option

        :return none:
        """

        self.name = name

        self.parentConfig = parentConfig

        self.subConfigs = []
        self.options = []

        # Add config to parent if given
        if self.parentConfig != None:
            self.parentConfig.addSubConfig(self)

    def addOption(self, option: Option):
        """Add an option to this level of configuration

        :param self:
            Self
        :param option:
            The option to add to this level of configuration

        :return none:
        """

        self.options.append(option)

    def addSubConfig(self, config: "Config"):
        """Add a sub-configuration for things nested inside of this
        configuration

        :param self:
            Self
        :param config:
            The Config to add to the list of sub-configs

        :return none:
        """

        self.subConfigs.append(config)

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
        for option in self.options:
            if option.name == name:
                return option.value

        # Ask the parent if they have the option
        if self.parentConfig != None:
            return self.parentConfig[name]

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
        for option in self.options:
            if option.name == name:
                option.value = newValue
                return

        # Ask the parent if they have the option
        if self.parentConfig != None:
            self.parentConfig[name] = newValue
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

        optionString = ""

        if self.options:
            optionString = optionString + "\n  "

        # Get the options for this config
        optionString = optionString + "\n  ".join(map(str, self.options))

        # Get lines from the subconfigs
        subConfigLines = "\n".join(map(str, self.subConfigs)).splitlines()

        # Append two spaces to the start of every line
        for i in range(0, len(subConfigLines)):
            subConfigLines[i] = "  {}".format(subConfigLines[i])

        subConfigString = "\n".join(subConfigLines)

        # Return the formatted string
        return "{}:{}\n{}".format(self.name, optionString, subConfigString)

    def load(self, data: dict):
        """Loads our values

        :param self:
            Self
        :param data:
            The data to load

        :return none
        """

        for key in data:
            # Load any options
            for option in self.options:
                if option.name == key:
                    option.value = data[key]
                    break
            else:
                # Load any sub configs
                for subConfig in self.subConfigs:
                    if subConfig.name == key:
                        subConfig.load(data[key])
                        break
                else:
                    raise Exception("Option \"{}\" not found in test config" + \
                         "(did you run generate after enabling?)".format(filename))

    def __iter__(self):
        """Iterates over configuration options

        :param self:
            Self

        :yield Tuple of String and object:
            The next option or the next configuration

        :return none:
        """

        # Yield the options
        for key in self.options:
            yield (key.name, key.value)

        # Yield the sub configs
        for subConfig in self.subConfigs:
            yield (subConfig.name, dict(subConfig))
