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

    This sub-module will provide access to a platforms GPIOs. An instance of a
    GPIO is referred to as a 'pin'.

    Pins can be accessed either by a familiar name or by their 'ID'. The list of
    available pin names and the meaning of a pin's ID are up to the platform
    implementing the Gpio sub-module class.

    This sub-module will offer access to all available pins by either their
    familiar name or their ID:

        modem.gpio[0] ...
        modem.gpio["mypin"] ...

    Pins can be individually controlled via their APIs. Pins can be controlled
    in bulk via the GPIO sub-module's APIs. Whether or not bulk operations are
    atomic is dependent on the platform.
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

        def __init__(self, id: int, name: str = None):
            """Creates a new pin

            :param self:
                Self
            :param id:
                The ID of this pin
            :param name:
                The name of this pin

            :return none:
            """

            self.name = name
            self.id = id

            self._gpio = None

        def setConfig(self, config: "Gpio.Config") -> None:
            """Configures a GPIO

            :param self:
                Self
            :param config:
                The configuration to use

            :return none:
            """

            self._gpio.setConfig(pins = [self], configs = [config])

        def getConfig(self) -> "Gpio.Config":
            """Gets a GPIO's configuration

            :param self:
                Self

            :return Gpio.Config:
                The GPIO's configuration
            """

            return self._gpio.getConfigs(pins = [self])[0]

        def write(self, state: int) -> None:
            """Writes a GPIO's output

            :param self:
                Self
            :param state:
                The output state to apply

            :return none:
            """

            self._gpio.write(pins = [self], states = [state])

        def read(self) -> int:
            """Reads a GPIO's state

            :param self:
                Self

            :param int:
                The pin's state
            """

            return self._gpio.read(pins = [self])[0]

    def __init__(self, pins: typing.List["Gpio.Pin"] = None) -> None:
        """Creates a new GPIO sub-module

        :param self:
            Self
        :param pins:
            Pins available on this modem

        :return none:
        """

        if pins is None:
            pins = []

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

    def __getitem__(self, key: typing.Union[int, str]) -> "Gpio.Pin":
        """Gets a pin by name or pin number

        :param self:
            Self
        :param key:
            Which item to get

        :raise TypeError:
            Invalid key type
        :raise KeyError:
            Failed to find pin

        :return Gpio.Pin:
            The pin
        """

        if isinstance(key, str):
            pins = [pin for pin in self._pins if pin.name == key]

        elif isinstance(key, int):
            pins = [pin for pin in self._pins if pin.id == key]

        else:
            raise TypeError(f"Invalid type {type(key)} for pin")

        if len(pins) < 1:
            raise KeyError(f"Failed to find {key} in pins")

        if len(pins) > 1:
            raise KeyError(f"{key} is ambiguous in pins")

        return pins[0]

    @staticmethod
    def _resolvePins(pins: typing.List[typing.Tuple[int, str]]) -> typing.List["Gpio.Pin"]:
        """Resolves pin references to actual pin objects

        :param pins:
            The pins to resolve to Gpio.Pin objects

        :raise KeyError:
            Invalid pin(s)

        :return typing.List[Gpio.Pin]:
            The resolved pins
        """

        return [self[pin] for pin in pins]

    def setConfigs(self, pins: typing.List[typing.Tuple[int, str]], configs: typing.List["Gpio.Config"]) -> None:
        """Configures GPIOs

        :param self:
            Self
        :param pins:
            The pins to configure
        :param configs:
            The configurations to use

        :return none:
        """

        self._setConfigs(pins = self._resolvePins(pins = pins), configs = configs)

    def getConfigs(self, pins: typing.List[typing.Tuple[int, str]]) -> typing.List["Gpio.Config"]:
        """Gets GPIO configurations

        :param self:
            Self
        :param pins:
            The GPIOs whose configurations to get

        :return List[Gpio.Config]:
            The GPIO configurations
        """

        self._getConfigs(pins = self._resolvePins(pins = pins))

    def write(self, pins: typing.List[typing.Tuple[int, str]], states: typing.List[int]) -> None:
        """Writes GPIO outputs

        :param self:
            Self
        :param pins:
            The pins whose output states to set
        :param states:
            The output states to apply

        :return none:
        """

        self._write(pins = self._resolvePins(pins = pins), states = states)

    def read(self, pins: typing.List[typing.Tuple[int, str]]) -> typing.List[int]:
        """Reads GPIO states

        :param self:
            Self
        :param pins:
            The pins whose states to read

        :param List[int]:
            The pin states
        """

        return self._read(pins = self._resolvePins(pins = pins))

    def _setConfigs(self, pins: typing.List["Gpio.Pin"], configs: typing.List["Gpio.Config"]) -> None:
        """Configures GPIOs

        :param self:
            Self
        :param pins:
            The pins to configure
        :param configs:
            The configurations to use

        :return none:
        """

        raise NotImplementedError(f"setConfigs() not implemented by {self.__class__.__name__}")

    def _getConfigs(self, pins: typing.List["Gpio.Pin"]) -> typing.List["Gpio.Config"]:
        """Gets GPIO configurations

        :param self:
            Self
        :param pins:
            The GPIOs whose configurations to get

        :return List[Gpio.Config]:
            The GPIO configurations
        """

        raise NotImplementedError(f"getConfigs() not implemented by {self.__class__.__name__}")

    def _write(self, pins: typing.List["Gpio.Pin"], states: typing.List[int]) -> None:
        """Writes GPIO outputs

        :param self:
            Self
        :param pins:
            The pins whose output states to set
        :param states:
            The output states to apply

        :return none:
        """

        raise NotImplementedError(f"write() not implemented by {self.__class__.__name__}")

    def _read(self, pins: typing.List["Gpio.Pin"]) -> typing.List[int]:
        """Reads GPIO states

        :param self:
            Self
        :param pins:
            The pins whose states to read

        :param List[int]:
            The pin states
        """

        raise NotImplementedError(f"read() not implemented by {self.__class__.__name__}")
