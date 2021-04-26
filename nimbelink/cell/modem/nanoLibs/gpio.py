###
 # \file
 #
 # \brief Skywire Nano GPIO resources
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

class Gpio:
    """Skywire Nano GPIO resources
    """

    Count   = 32
    """The number of available GPIOs on a Skywire Nano"""

    Output  = 0
    Input   = 1
    """Configuration values for GPIOs"""

    def __init__(self, nano):
        """Creates a new GPIO sub-module

        :param self:
            Self
        :param nano:
            The Skywire Nano we're attached to

        :return none:
        """

        self._nano = nano

    def _makeParameters(self, gpios, things = None):
        """Makes GPIO masks or single values for an operation

        :param self:
            Self
        :param gpios:
            The GPIOs to do this for
        :param things:
            The values being applied to the GPIOs

        :return Tuple of Strings:
            The GPIO and thing parameters
        """

        thingMask = None

        # If this is just a single set, use the single GPIO setter
        if len(gpios) < 2:
            gpioMask = "{}".format(gpios[0])

            if things != None:
                thingMask = "{}".format(things[0])

        # Else, send the mask
        else:
            gpioMask = [0] * self.Count

            if things != None:
                thingMask = [0] * self.Count

            # The GPIOs can be in any order, so stick their things into the
            # correct positions
            #
            # Note that we're using little-endian ordering for our natural
            # lists, but our mask string will need big-endian ordering for bits
            # (as if printing an integer in binary), so we'll need to reverse
            # the lists when done before making the string.
            for i in range(len(gpios)):
                gpioMask[gpios[i]] = 1

                if things != None:
                    thingMask[gpios[i]] = things[i]

            gpioMask.reverse()
            gpioMask = "".join([str(gpio) for gpio in gpioMask])

            if things != None:
                thingMask.reverse()
                thingMask = "".join([str(thing) for thing in thingMask])

        return (gpioMask, thingMask)

    def _parseParameter(self, gpios, thing):
        """Parses a GPIO response

        :param self:
            Self
        :param gpios:
            The GPIOs from the original command
        :param thing:
            The response to the command

        :return :
        """

        # The string in the response will be in bitwise order -- as if printing
        # an integer in binary form -- but our indexing will be the opposite, as
        # we're using it like an array, so make an array of the response's
        # characters and reverse it
        values = [int(value) for value in thing]
        values.reverse()

        # If there's just the one GPIO, the response might've been either a mask
        # or a single value, depending on how exactly the command was sent
        if len(gpios) < 2:
            # If there's only one value in the response, use it as-is
            if len(values) < 2:
                return values

            # Else, use the value for the GPIO
            else:
                return [values[gpios[0]]]

        states = [None] * len(gpios)

        # Get the states of each GPIO we queried
        for i in range(len(gpios)):
            # If this GPIO isn't in the response value, that's a paddlin'
            if gpios[i] >= len(values):
                return None

            states[i] = int(values[gpios[i]])

        return states

    def setConfigs(self, gpios, configs):
        """Configures GPIOs as inputs and/or outputs

        :param self:
            Self
        :param gpios:
            A list of the GPIOs to change
        :param configs:
            A list of the configurations to set the GPIOs to

        :raise ValueError:
            GPIO and configuration lists do not match

        :return True:
            GPIOs configured
        :return False:
            Failed to configure GPIOs
        """

        # Make sure their lists are the same length
        if len(gpios) != len(configs):
            raise ValueError("Need matching GPIOs and states")

        # Get the parameters for this
        gpioParam, configParam = self._makeParameters(gpios, configs)

        # Configure the GPIOs
        response = self._nano.at.sendCommand("AT#GPIO={},2,{}".format(gpioParam, configParam))

        # If that failed, that's a paddlin'
        if not response:
            return False

        return True

    def getConfigs(self, gpios):
        """Gets GPIO configurations

        :param self:
            Self
        :param gpios:
            A list of the GPIOs to query

        :return None:
            Always
        """

        # Not supported by the Skywire Nano
        return None

    def write(self, gpios, states):
        """Writes GPIO outputs

        :param self:
            Self
        :param gpios:
            A list of the GPIOs to change
        :param states:
            A list of the states to set the respective GPIOs to

        :raise ValueError:
            GPIO and state lists do not match

        :return True:
            GPIOs set
        :return False:
            Failed to set GPIOs
        """

        # Make sure their lists are the same length
        if len(gpios) != len(states):
            raise ValueError("Need matching GPIOs and states")

        # Get the parameters for this
        gpioParam, stateParam = self._makeParameters(gpios, states)

        # Set the GPIO states
        response = self._nano.at.sendCommand("AT#GPIO={},1,{}".format(gpioParam, stateParam))

        # If that failed, that's a paddlin'
        if not response:
            return False

        return True

    def read(self, gpios):
        """Reads GPIO states

        :param self:
            Self
        :param gpios:
            A list of the GPIOs to query

        :return None:
            Failed to query GPIO states
        :return Array of Integers:
            The GPIO states
        """

        # Get the parameters for this
        gpioParam, _ = self._makeParameters(gpios)

        # Query the GPIO states
        response = self._nano.at.sendCommand("AT#GPIO={},0".format(gpioParam))

        # If that failed, that's a paddlin'
        if not response:
            return None

        # If the response doesn't have an output, that's a paddlin'
        if len(response.output) < 1:
            return None

        # The response is in the form of '#GPIO: <value(s)>'
        fields = response.output.split(":")

        # If that's not the case, that's a paddlin'
        if len(fields) != 2:
            return None

        # Parse the response and get the states
        return self._parseParameter(gpios, fields[1].strip())
