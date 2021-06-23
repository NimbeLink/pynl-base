"""
A YAML-based configuration storage backend

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import yaml

try:
    # Try to use the libyaml bindings
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper

except ImportError:
    # Fall back to pure python yaml library
    from yaml import Loader
    from yaml import Dumper

from .backend import Backend

class YamlBackend(Backend):
    """A YAML-based configuration storage backend
    """

    def __init__(self, filename: str = "config.yaml") -> None:
        """Creates a new YAML backend

        :param self:
            Self
        :param filename:
            The YAML file to use

        :return none:
        """

        self._filename = filename

    def getDict(self) -> dict:
        """Gets a file's dictionary of data

        :param self:
            Self

        :raise OSError:
            Failed to get dictionary from file

        :return dict:
            The dictionary of data
        """

        # Try to open the previous config file
        try:
            with open(self._filename, "r") as configFile:
                # Read in existing configuration
                data = yaml.load(configFile, Loader = Loader)

        # If the file doesn't exist, use an empty configuration
        except FileNotFoundError:
            raise OSError(f"Failed to load file {self._filename}")

        # If there wasn't any data, use an empty configuration
        if data == None:
            raise OSError(f"No data found in file {self._filename}")

        return data

    def setDict(self, data: dict) -> None:
        """Sets a file's dictionary of data

        :param self:
            Self
        :param data:
            The data to save

        :return none:
        """

        # Write the config to disk
        with open(self._filename, "w") as configFile:
            yaml.dump(data, configFile, Dumper = Dumper)
