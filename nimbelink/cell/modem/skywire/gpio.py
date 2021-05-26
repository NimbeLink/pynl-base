"""
Skywire modem GPIO utilities

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

class Gpio:
    """Skywire modem GPIO utilities
    """

    Count = 0
    """How many GPIOs this modem offers
    """

    class Config:
        """Configurations for GPIOs
        """

        Output  = 0
        Input   = 1

    class PinMap:
        """A mapping of physical pins to qualitative accessors
        """

        def __init__(self, name: str, pin: int):
            """Creates a new pin map

            :param self:
                Self
            :param name:
                The name of this pin
            :param pin:
                The index of this pin

            :return none:
            """

            self.name = name
            self.pin = pin

    def setConfigs(self, pins: typing.List[int], configs: typing.List[Gpio.Config]) -> None:
        """Configures GPIOs

        :param self:
            Self
        :param pins:
            The pins to configure
        :param configs:
            The configurations to use

        :return none:
        """

        raise NotImplementedError("setConfigs() not implemented by {}".format(self.__class__.__name__))

    def getConfigs(self, pins: typing.List[int]) -> typing.List[Gpio.Config]:
        """Gets GPIO configurations

        :param self:
            Self
        :param pins:
            The GPIOs whose configurations to get

        :return List[Gpio.Config]:
            The GPIO configurations
        """

        raise NotImplementedError("getConfigs() not implemented by {}".format(self.__class__.__name__))

    def write(self, pins: typing.List[int], states: typing.List[int]) -> None:
        """Writes GPIO outputs

        :param self:
            Self
        :param pins:
            The pins whose output states to set
        :param states:
            The output states to apply

        :return none:
        """

        raise NotImplementedError("write() not implemented by {}".format(self.__class__.__name__))

    def read(self, pins: typing.List[int]) -> states: typing.List[int]:
        """Reads GPIO states

        :param self:
            Self
        :param pins:
            The pins whose states to read

        :param List[int]:
            The pin states to apply
        """

        raise NotImplementedError("read() not implemented by {}".format(self.__class__.__name__))
