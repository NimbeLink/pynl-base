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

    The GPIO class itself presents APIs for using GPIOs via only their pin
    number. The GPIO class also provides a means for looking up GPIOs either by
    pin number or by name, thus allowing translation between pin number and
    name, as well as direct GPIO APIs (i.e. those found in the Pin class below).
    """

    class Config:
        """Configurations for GPIOs
        """

        Output  = 0
        Input   = 1

    class Pin:
        """A physical pin

        Implementors of the base Gpio class do not need to implement the Pin
        class. The base GPIO handling will manage setting up its list of pins at
        instantiation such that instantiations of the Pin class are ready to be
        used in any specific context.

        This class is used as a wrapper around a single pin that facilitates
        passing an API back to the pin's parent Gpio instance.
        """

        def __init__(self, pin: int, name: str = None):
            """Creates a new pin map

            :param self:
                Self
            :param pin:
                The index of this pin
            :param name:
                The name of this pin

            :return none:
            """

            self.name = name
            self.pin = pin

            # We expect to have our GPIO module filled in for us by our parent
            # Gpio instance
            self._gpio = None

        def setConfig(self, config: "Gpio.Config") -> None:
            """Configures a GPIO

            :param self:
                Self
            :param config:
                The configuration to use

            :return none:
            """

            self._gpio.setConfig(pins = [self.pin], configs = [config])

        def getConfig(self) -> "Gpio.Config":
            """Gets a GPIO's configuration

            :param self:
                Self

            :return Gpio.Config:
                The GPIO's configuration
            """

            return self._gpio.getConfigs(pins = [self.pin])[0]

        def write(self, state: int) -> None:
            """Writes a GPIO's output

            :param self:
                Self
            :param state:
                The output state to apply

            :return none:
            """

            self._gpio.write(pins = [self.pin], states = [state])

        def read(self) -> int:
            """Reads a GPIO's state

            :param self:
                Self

            :param int:
                The pin's state
            """

            return self._gpio.read(pins = [self.pin])[0]

    def __init__(self, pins: typing.List["Gpio.Pin"] = None) -> None:
        """Creates a new GPIO sub-module

        :param self:
            Self
        :param pins:
            Pins available on this modem

        :return none:
        """

        if pins == None:
            pins = []

        # We want our incoming pins to be able to reference our APIs for
        # fulfilling API requests, so fill in their internal gpio member
        for pin in pins:
            pin._gpio = self

        self._pins = pins

    def __len__(self) -> int:
        """Gets the number of pins available

        :param self:
            Self

        :return int:
            The number of pins available
        """

        return len(self._pins)

    def __getitem__(self, key: typing.Union[int, str]) -> "Gpio.PinMap":
        """Gets a pin by name or pin number

        :param self:
            Self
        :param key:
            Which item to get

        :raise IndexError:
            Failed to find pin

        :return Gpio.Pin:
            The pin
        """

        if isinstance(key, str):
            pins = [pin for pin in self._pins if pin.name == key]

        elif isinstance(key, int):
            pins = [pin for pin in self._pins if pin.name == key]

        else:
            raise TypeError("Invalid type {} for pin mapping access".format(type(key)))

        if len(pins) < 1:
            raise KeyError("Failed to find {} in pin maps".format(key))

        if len(pins) > 1:
            raise KeyError("{} is ambiguous in pin maps".format(key))

        return pins[0]

    def setConfigs(self, pins: typing.List[int], configs: typing.List["Gpio.Config"]) -> None:
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

    def getConfigs(self, pins: typing.List[int]) -> typing.List["Gpio.Config"]:
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

    def read(self, pins: typing.List[int]) -> typing.List[int]:
        """Reads GPIO states

        :param self:
            Self
        :param pins:
            The pins whose states to read

        :param List[int]:
            The pin states
        """

        raise NotImplementedError("read() not implemented by {}".format(self.__class__.__name__))
