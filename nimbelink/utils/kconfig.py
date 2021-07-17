"""
A Kconfig configuration

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

class Kconfig:
    """A Kconfig configuration
    """

    FileName = ".config"
    """A typical Kconfig output filename"""

    NamePrefix = "CONFIG_"
    """The prefix all configuration names start with"""

    @staticmethod
    def makeFromConfig(fileName: str) -> "Kconfig":
        """Makes a Kconfig configuration from a file

        :param fileName:
            The file whose configurations to parse

        :return TypeError:
            Failed to parse file

        :return Kconfig:
            The configuration
        """

        configurations = {}

        with open(fileName, "r") as file:
            for line in file.readlines():
                # If this configuration's name doesn't start with our prefix,
                # skip it
                if not line.startswith(Kconfig.NamePrefix):
                    continue

                # Get rid of the line ending
                line = line.rstrip()

                # Get the name of the configuration and its value
                fields = line.split("=")

                # If we couldn't unpack the fields, this is an invalid Kconfig
                # file
                if len(fields) < 2:
                    raise TypeError(f"Invalid Kconfig line '{line}' in '{fileName}'")

                # It's possible the value of this configuration has a '=' in it,
                # so make sure any value fields are joined back together
                name = fields[0][len(Kconfig.NamePrefix):]
                value = "=".join(fields[1:])

                # In case the string was enclosed in quotes, remove those
                #
                # We'll store them as native strings here in Python-land.
                value = value.rstrip("\"").lstrip("\"")

                # Got another configuration
                configurations[name] = value

        return Kconfig(configurations = configurations)

    def __init__(self, configurations: dict = None) -> None:
        """Creates a new Kconfig configuration

        :param self:
            Self
        :param configurations:
            The configurations to use

        :return none:
        """

        if configurations is None:
            configurations = {}

        self._configurations = configurations

    def __getitem__(self, name: str) -> object:
        """Get a configuration

        :param self:
            Self
        :param name:
            The name of the configuration to get

        :raise KeyError:
            Configuration not found

        :return object:
            The configuration value
        """

        return self._configurations[name]

    def __contains__(self, name: str) -> bool:
        """Gets if we contain a configuration

        :param self:
            Self
        :param name:
            The name of the configuration to check for

        :return True:
            We contain the configuration
        :return False:
            We do not contain the configuration
        """

        return name in self._configurations

    def __str__(self) -> str:
        """Gets a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        string = ""

        for thing in self._configurations.items():
            string += f"{thing}\n"

        return string[:-1]
