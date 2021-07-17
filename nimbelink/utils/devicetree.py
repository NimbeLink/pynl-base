"""
A Devicetree configuration

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from .kconfig import Kconfig

class Devicetree(Kconfig):
    """A Devicetree configuration

    This is essentially the same as a Kconfig object, just with different
    parsing of the underlying file.
    """

    FileName = "devicetree_legacy_unfixed.h"
    """A typical Devicetree output filename"""

    NamePrefix = "#define DT_"
    """The prefix all configuration names start with"""

    @staticmethod
    def makeFromConfig(fileName: str) -> "Devicetree":
        """Makes a Devicetree configuration from a file

        :param fileName:
            The file whose configurations to parse

        :return TypeError:
            Failed to parse file

        :return Devicetree:
            The configuration
        """

        configurations = {}

        with open(fileName, "r") as file:
            for line in file.readlines():
                # If this configuration's name doesn't start with our prefix,
                # skip it
                if not line.startswith(Devicetree.NamePrefix):
                    continue

                # Get rid of the line ending
                line = line.rstrip()

                # Get the name of the configuration and its value
                fields = [field for field in line.split(" ") if len(field) > 0]

                # If we couldn't unpack the fields, this is an invalid
                # Devicetree file
                if len(fields) < 3:
                    raise TypeError(f"Invalid Devicetree line '{line}' in '{fileName}'")

                # This is C-include-compatible code, so we shouldn't need to do
                # any funny business
                name = fields[1]
                value = fields[2]

                # If this field already exists, don't add it again
                if name in configurations:
                    continue

                # Try to get the integer value for this configuration
                try:
                    value = int(value)

                # If this field is referencing another configuration, resolve
                # that configuration's value for this new entry
                except ValueError:
                    if value in configurations:
                        value = configurations[value]

                    else:
                        continue

                # Got another configuration
                configurations[name] = value

        return Devicetree(configurations = configurations)
