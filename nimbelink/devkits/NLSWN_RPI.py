"""
Defines helpers for interacting with the Nano Raspberry Pi HAT

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""
import time
import typing

# Try importing the RPi.GPIO library
# NOTE: pylint might give errors for this module that don't actually exist
import RPi.GPIO

import nimbelink.devkits.host as host

# TODO: Get a product name for Ian's Raspberry Pi HAT
class NLSWN_RPI(host.Host):
    """Use the GPIO pins on the raspberry pi to read and drive the GPIO pins
    on the Nano
    """

    class GPIO(host.Host.GPIO):
        """GPIO pin control and configuration for the NLSWN_RPI HAT
        """

        # Map of Nano pins to Raspberry Pi pins
        PINS = {
            # Nano Pin : (Raspberry Pi Pin, Mode)
            "IO5": (21, RPi.GPIO.OUT),
            "nRESET": (20, RPi.GPIO.IN),
        }

        def __init__(self):
            super().__init__()
            # Set the pin naming scheme to the BCM scheme
            RPi.GPIO.setmode(RPi.GPIO.BCM)

            # Initialize all of the defined pins
            for nanoPin in self.PINS:
                RPi.GPIO.setup(self.PINS[nanoPin][0], self.PINS[nanoPin][1])

        def read(self, gpioPin: typing.Union[int, str]) -> bool:
            """Read the state of a GPIO pin on the NLSWN_RPI host

            :param gpioPin: The name or number of the GPIO pin on the Nano

            :return: The state of the host pin
            :rtype: bool
            """

            if isinstance(gpioPin, str):
                # By name
                return RPi.GPIO.input(self.PINS[gpioPin][0])
            elif isinstance(gpioPin, int):
                # By number
                pinString = "IO{}".format(gpioPin)
                return RPi.GPIO.input(self.PINS[pinString][0])
            else:
                raise TypeError("{}.read() doesn't take {}!"
                                .format(self.__class__.__name__, type(gpioPin)))

        def write(self, gpioPin: typing.Union[int, str], state: bool) -> None:
            """Manipulate the state of a host pin connected to the pin
            specified by gpioPin

            :param gpioPin:
                The name or number of the pin on the Nano

            :return: None
            :rtype: None
            """
            if isinstance(gpioPin, str):
                # By name
                RPi.GPIO.output(self.PINS[gpioPin][0], state)
            elif isinstance(gpioPin, int):
                # By number
                pinString = "IO{}".format(gpioPin)
                RPi.GPIO.output(self.PINS[pinString][0], state)
            else:
                raise TypeError("{}.write() doesn't take {}!"
                                .format(self.__class__.__name__, type(gpioPin)))

    def __init__(self) -> None:
        super().__init__()

        self._gpio = self.GPIO()

    def reset(self) -> None:
        """Resets the modem by pulling the nRESET pin low

        :param self:
            Self

        :return: None
        :rtype: None
        """

        # TODO: Until we get a MOSFET/Transistor onto the HAT we have to set to
        # output, then reset to input. This will be replaced with calls
        # to read()/write()

        # Set the reset pin low
        RPi.GPIO.setup(
            self._gpio.PINS["nRESET"][0],
            RPi.GPIO.OUT,
            initial=False
        )
        time.sleep(0.05)
        # Reset the reset pin to an input
        RPi.GPIO.setup(self._gpio.PINS["nRESET"][0], RPi.GPIO.IN)

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, exceptionTraceback):
        # Clean up the GPIO
        RPi.GPIO.cleanup()

    def __del__(self):
        # Clean up the GPIO
        RPi.GPIO.cleanup()
