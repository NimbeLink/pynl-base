"""
Skywire Nano GPIO resources

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import nimbelink.cell.modem as modem
import nimbelink.cell.modem.skywire as skywire

class Gpio(skywire.Gpio):
    """Skywire Nano GPIO resources
    """

    def __init__(self, nano):
        """Creates a new GPIO sub-module

        :param self:
            Self
        :param nano:
            The Skywire Nano we're attached to

        :return none:
        """

        # Make a simple pin for each of our 32 GPIOs
        super(Gpio, self).__init__(
            pins = [skywire.Gpio.Pin(pin = i) for i in range(32)]
        )

        self._nano = nano

    def _makeParameters(self, pins, things = None):
        """Makes GPIO masks or single values for an operation

        :param self:
            Self
        :param pins:
            The GPIOs to do this for
        :param things:
            The values being applied to the GPIOs

        :return Tuple of Strings:
            The GPIO and thing parameters
        """

        thingMask = None

        # If this is just a single set, use the single GPIO setter
        if len(pins) < 2:
            gpioMask = f"{pins[0]}"

            if things != None:
                thingMask = f"{things[0]}"

        # Else, send the mask
        else:
            gpioMask = [0] * len(self)

            if things != None:
                thingMask = [0] * len(self)

            # The GPIOs can be in any order, so stick their things into the
            # correct positions
            #
            # Note that we're using little-endian ordering for our natural
            # lists, but our mask string will need big-endian ordering for bits
            # (as if printing an integer in binary), so we'll need to reverse
            # the lists when done before making the string.
            for i in range(len(pins)):
                gpioMask[pins[i]] = 1

                if things != None:
                    thingMask[pins[i]] = things[i]

            gpioMask.reverse()
            gpioMask = "".join([str(gpio) for gpio in gpioMask])

            if things != None:
                thingMask.reverse()
                thingMask = "".join([str(thing) for thing in thingMask])

        return (gpioMask, thingMask)

    def _parseParameter(self, pins, thing):
        """Parses a GPIO response

        :param self:
            Self
        :param pins:
            The GPIOs from the original command
        :param thing:
            The response to the command

        :return None:
            Failed to parse parameters
        :return Array of Integers:
            The GPIO thing values
        """

        # The string in the response will be in bitwise order -- as if printing
        # an integer in binary form -- but our indexing will be the opposite, as
        # we're using it like an array, so make an array of the response's
        # characters and reverse it
        values = [int(value) for value in thing]
        values.reverse()

        # If there's just the one GPIO, the response might've been either a mask
        # or a single value, depending on how exactly the command was sent
        if len(pins) < 2:
            # If there's only one value in the response, use it as-is
            if len(values) < 2:
                return values

            # Else, use the value for the GPIO
            else:
                return [values[pins[0]]]

        states = [None] * len(pins)

        # Get the states of each GPIO we queried
        for i in range(len(pins)):
            # If this GPIO isn't in the response value, that's a paddlin'
            if pins[i] >= len(values):
                return None

            states[i] = int(values[pins[i]])

        return states

    def setConfigs(self, pins, configs):
        """Configures GPIOs as inputs and/or outputs

        :param self:
            Self
        :param pins:
            A list of the GPIOs to change
        :param configs:
            A list of the configurations to set the GPIOs to

        :raise ValueError:
            GPIO and configuration lists do not match
        :raise AtError:
            Failed to configure GPIOs

        :return none:
        """

        # Make sure their lists are the same length
        if len(pins) != len(configs):
            raise ValueError("Need matching GPIOs and states")

        # Get the parameters for this
        gpioParam, configParam = self._makeParameters(pins, configs)

        # Configure the GPIOs
        response = self._nano.at.sendCommand(f"AT#GPIO={gpioParam},2,{configParam}")

        # If that failed, that's a paddlin'
        if not response:
            raise modem.AtError(response)

    def getConfigs(self, pins):
        """Gets GPIO configurations

        :param self:
            Self
        :param pins:
            A list of the GPIOs to query

        :raise AtError:
            Always
        """

        # Not supported by the Skywire Nano
        raise modem.AtError(None, "Skywire Nano GPIO configuration getting not supported")

    def write(self, pins, states):
        """Writes GPIO outputs

        :param self:
            Self
        :param pins:
            A list of the GPIOs to change
        :param states:
            A list of the states to set the respective GPIOs to

        :raise ValueError:
            GPIO and state lists do not match
        :raise AtError:
            Failed to set GPIOs

        :return none:
        """

        # Make sure their lists are the same length
        if len(pins) != len(states):
            raise ValueError("Need matching GPIOs and states")

        # Get the parameters for this
        gpioParam, stateParam = self._makeParameters(pins, states)

        # Set the GPIO states
        response = self._nano.at.sendCommand(f"AT#GPIO={gpioParam},1,{stateParam}")

        # If that failed, that's a paddlin'
        if not response:
            raise modem.AtError(response)

    def read(self, pins):
        """Reads GPIO states

        :param self:
            Self
        :param pins:
            A list of the GPIOs to query

        :raise AtError:
            Failed to query GPIO states

        :return Array of Integers:
            The GPIO states
        """

        # Get the parameters for this
        gpioParam, _ = self._makeParameters(pins)

        # Query the GPIO states
        response = self._nano.at.sendCommand(f"AT#GPIO={gpioParam},0")

        # If that failed, that's a paddlin'
        if not response:
            raise modem.AtError(response)

        lines = response.lines

        # If the response doesn't have an output, that's a paddlin'
        if len(lines) < 1:
            raise modem.AtError(response, "GPIO states not in response")

        # The response is in the form of '#GPIO: <value(s)>'
        fields = lines[0].split(":")

        # If that's not the case, that's a paddlin'
        if len(fields) != 2:
            raise modem.AtError(response, "Invalid GPIO states")

        # Parse the response and get the states
        return self._parseParameter(pins, fields[1].strip())
