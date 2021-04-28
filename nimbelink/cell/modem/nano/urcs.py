###
 # \file
 #
 # \brief Skywire Nano URCs
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import nimbelink.cell.modem as modem

class Urcs:
    """Skywire Nano URCs
    """

    class Dfu:
        """A Device Firmware Update (DFU) URC
        """

        Prefix = "DFU"
        """The prefix to a DFU URC"""

        class Type:
            Failure     = 0
            """A failure has occurred"""

            Done        = 1
            """DFU is finished"""

            Progress    = 2
            """DFU progress was made"""

            Applying    = 3
            """DFU is now applying the update"""

        def __init__(self, type, value = None):
            """Creates a new DFU URC

            :param self:
                Self
            :param type:
                The type of DFU URC this is
            :param value:
                A value for the URC, if any

            :return none:
            """

            self.type = type
            self.value = value

        @staticmethod
        def makeFromString(string):
            """Creates a DFU URC from a string

            :param string:
                The string to parse

            :raise AtError:
                Failed to parse DFU URC

            :return Urcs.Dfu:
                The parsed DFU URC
            """

            # Split the string into the prefix and its contents
            fields = string.split(":")

            # If that failed, that's a paddlin'
            if len(fields) != 2:
                raise modem.AtError(string, "DFU URC missing prefix")

            # Make sure this is ours
            if fields[0].strip() != Urcs.Dfu.Prefix:
                raise modem.AtError(string, "Invalid DFU URC prefix")

            # Try to split the contents into a type and a value
            fields = fields[1].strip().split(",")

            # Get the type
            try:
                type = int(fields[0])

            except ValueError:
                raise modem.AtError(string, "Invalid DFU URC type")

            # If there was a value, get it
            if len(fields) > 1:
                try:
                    value = int(fields[1])

                except ValueError:
                    raise modem.AtError(string, "Invalid DFU URC value")

            else:
                value = None

            # Make sure we have a value if we need one
            if (((type == Urcs.Dfu.Type.Failure) or (type == Urcs.Dfu.Type.Progress)) and
                (value == None)
            ):
                raise modem.AtError(None, "DFU URC missing value")

            return Urcs.Dfu(type = type, value = value)
