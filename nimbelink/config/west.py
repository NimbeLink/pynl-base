"""
A west-based configuration storage backend

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import subprocess
import west.configuration

from .backend import Backend

class WestBackend(Backend):
    """A west-based configuration storage backend
    """

    def __init__(self, rootName: str = "nimbelink") -> None:
        """Creates a new YAML backend

        :param self:
            Self
        :param rootName:
            A root namespace to tuck configurations under

        :return none:
        """

        self._rootName = rootName

    def getDict(self) -> dict:
        """Gets a file's dictionary of data

        :param self:
            Self

        :raise OSError:
            Failed to get dictionary from 'west'

        :return dict:
            The dictionary of data
        """

        data = {}

        # Get our configurations
        try:
            configurations = subprocess.check_output(["west", "config", "-l"]).decode()

        except subprocess.CalledProcessError:
            raise OSError("Failed to get west configurations")

        # Parse each line
        for line in configurations.split():
            fields = line.split("=", maxsplit = 1)

            # If we didn't get a properly-formatted line, that's a paddlin'
            if len(fields) != 2:
                raise OSError(f"Failed to parse west configuration '{line}'")

            # Note the value
            value = fields[1]

            # Get our namespaces and option name, which are separated by a '.'
            fields = fields[0].split(".")

            # The option is everything after the first '.'
            option = fields.pop(-1)

            # Get our namespaces, which are separated by a ':' and precede the
            # first '.'
            namespaces = "".join(fields).split(":")

            # If the first namespace is not us, skip it
            if (len(namespaces) < 1) or (namespaces[0] != self._rootName):
                continue

            # Replace our root name with a real 'root' entry
            namespaces[0] = "root"

            # Start wandering down the namespaces starting from the top
            nextData = data

            for namespace in namespaces:
                # If this namespace hasn't been added yet, add it
                if namespace not in nextData:
                    nextData[namespace] = {}

                # Move to that namespace for next time
                nextData = nextData[namespace]

            # Add our option and its value
            nextData[option] = value

        return data

    def setDict(self, data: dict) -> None:
        """Sets a file's dictionary of data

        :param self:
            Self
        :param data:
            The data to save

        :return none:
        """

        pass

    @staticmethod
    def _getLines(data: dict) -> None:
        """Generates west configuration-formatted lines for a dictionary

        :param dict:
            The data to format strings for

        :yield str:
            The next line

        :return none:
        """

        for key in data:
            # If this is a sub-config, recursively call our formatter on the
            # sub-config and append our own configuration name (the current key)
            # to the beginning of the line, and then return that as the next
            # line
            if isinstance(data[key], dict):
                for line in WestBackend._getLines(data = data[key]):
                    yield f":{key}{line}"

            # Else, this must be an option, so yield our next line using our key
            # and the option's value
            else:
                yield f".{key}={data[key]}"

    def format(self, data: dict) -> str:
        """Gets a string representation of a dictionary

        :param self:
            Self
        :param data:
            The data to format a string for

        :return str:
            The formatted string
        """

        lines = []

        for line in WestBackend._getLines(data = data):
            lines.append(f"{self._rootName}{line}")

        return "\n".join(lines)
