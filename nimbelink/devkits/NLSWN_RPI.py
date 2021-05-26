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
#
# Note: pylint might give errors for this module if it doesn't actually exist.
import RPi.GPIO

import nimbelink.cell.modem.skywire as skywire

class NLSWN_RPI(skywire.Host):
    """Use the GPIO pins on the raspberry pi to read and drive the GPIO pins on
    the Nano
    """

    class Gpio(skywire.Gpio):
        """GPIO pin control and configuration for the NLSWN_RPI HAT
        """

        def __init__(self):
            """Creates a new GPIO module

            :param self:
                Self

            :return none:
            """

            super(NLSWN_RPI.Gpio, self).__init__(
                pins = [
                    skywire.Gpio.Pin(
                        pin = 21,
                        name = "IO5"
                    ),
                    skywire.Gpio.Pin(
                        pin = 20,
                        name = "nRESET"
                    )
                ]
            )

            # Set the pin naming scheme to the BCM scheme
            RPi.GPIO.setmode(RPi.GPIO.BCM)

            # Initialize all of the defined pins
            RPi.GPIO.setup(self["IO5"].pin, RPi.GPIO.OUT)
            RPi.GPIO.setup(self["nRESET"].pin, RPi.GPIO.IN)

    def read(self, pins: typing.List[int]) -> typing.List[int]:
        """Read the state of a GPIO pin on the NLSWN_RPI host

        :param self:
            Self
        :param pins:
            The host pins to read

        :return List[int]:
            The states of the host pins
        """

        return [RPi.GPIO.input(pin.pin) for pin in pins]

    def write(self, pins: typing.List[int], states: typing.List[int]) -> None:
        """Manipulate the state of a host pin connected to the pin specified by
        pin

        :param self:
            Self
        :param pins:
            The pins to write
        :param states:
            The states to set the pins to

        :return none:
        """

        for i in range(len(pins)):
            RPi.GPIO.output(pins[i].pin, states[i])

    def __init__(self) -> None:
        """Creates a new NLSWN RPI

        :param self:
            Self

        :return none:
        """

        super().__init__(gpio = NLSWN_RPI.Gpio())

    def reset(self) -> None:
        """Resets the modem by pulling the nRESET pin low

        :param self:
            Self

        :return none:
        """

        # TODO: Until we get a MOSFET/Transistor onto the HAT we have to set to
        # output, then reset to input. This will be replaced with calls to
        # read()/write()

        # Set the reset pin low
        RPi.GPIO.setup(
            self.gpio["nRESET"].pin,
            RPi.GPIO.OUT,
            initial = False
        )

        time.sleep(0.05)

        # Reset the reset pin to an input
        RPi.GPIO.setup(self.gpio["nRESET"].pin, RPi.GPIO.IN)

    def __enter__(self):
        """Enters the NLSWN RPI as a context

        :param self:
            Self

        :return NLSWN_RPI:
            Us
        """

        return self

    def __exit__(self, exceptionType, exceptionValue, exceptionTraceback):
        """Exits the NLSWN RPI context

        :param self:
            Self
        :param exceptionType:
            The exception type, if any
        :param exceptionValue:
            The exception value, if any
        :param exceptionTraceback:
            The exception traceback, if any

        :return none:
        """

        # Clean up the GPIO
        RPi.GPIO.cleanup()

    def __del__(self):
        """Deletes the NLSWN RPI

        :param self:
            Self

        :return none:
        """

        # Clean up the GPIO
        RPi.GPIO.cleanup()
