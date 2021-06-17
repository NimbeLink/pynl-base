"""
Defines a base class for interacting with platforms hosting a modem

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

from nimbelink.cell.modem.skywire.gpio import Gpio

class Host:
    """This class defines basic methods that a host shall provide in order to
    interact with a modem

    A host is a device that interacts with a modem. For instance a Raspberry Pi
    with a Skywire Development Kit attached could be considered a host.
    """

    def __init__(self, gpio: Gpio) -> None:
        """Creates a new host

        :param self:
            Self
        :param gpio:
            A Skywire modem GPIO-like sub-module for controlling host GPIOs

        :return none:
        """

        self._gpio = gpio

    @property
    def gpio(self) -> Gpio:
        """Access the gpio pins of the host

        :param self:
            Self

        :return Gpio:
            Our GPIO
        """

        return self._gpio

    def reset(self) -> None:
        """Reset the modem using power and/or control pins

        Must be driven with an open drain or open collector signal. Pull the pin
        to GND to reset.

        Refer to Skywire Hardware Developers Guide for more information.

        :param self:
            Self

        :return none:
        """

        raise NotImplementedError(f"reset() not implemented by {self.__class__.__name__}")
