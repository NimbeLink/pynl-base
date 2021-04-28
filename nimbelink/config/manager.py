###
 # \file
 #
 # \brief A configuration manager
 #
 # (C) NimbeLink Corp. 2021
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import yaml

try:
    # Try to use the libyaml bindings
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper

except ImportError:
    # Fall back to pure python yaml library
    from yaml import Loader
    from yaml import Dumper

from nimbelink.config.config import Config
from nimbelink.config.config import Option

class ConfigManager:
    """A configuration manager
    """

    def __init__(self):
        """Creates a new configuration manager

        :param self:
            Self

        :return None:
        """

        self.root = Config("root")

    def generate(self, filename: str = "config.yaml"):
        """Generates a new configuration

        :param self:
            Self
        :param filename:
            The file to save the configuration to

        :return None:
        """

        # Try to open the previous config file
        try:
            with open(filename, "r") as configFile:
                # Read in past config
                data = yaml.load(configFile, Loader=Loader)
                print(data)
                self.root.load(data)

        except FileNotFoundError:
            print("Unable to open past config \"{}\", generating new config".format(filename))

        # Write the config to disk
        with open(filename, "w") as configFile:
            yaml.dump(dict(self.root), configFile, Dumper=Dumper)
