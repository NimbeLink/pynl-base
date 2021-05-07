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

class Host:
    """This class defines basic methods that a host shall provide in order to
    interact with a modem

    A host is a device that interacts with a modem. For instance a Raspberry Pi
    with a Skywire Development Kit attached could be considered a host.
    """
    class GPIO:
        """
        """

        def __init__(self):
            pass

        def read(self, gpioPin: typing.Union[int, str]) -> bool:
            """Read the state of a host's GPIO pin
            
            :param gpioPin:
                The schematic name of the pin or a pin number on the modem

            :return: The state of the host's GPIO pin
            :rtype: bool
            """

            raise NotImplementedError("{} doesn't implement read()!"
                                    .format(self.__class__.__name__))

        def write(self, gpioPin: typing.Union[int, str], state: bool) -> None:
            """Write the state of a host's GPIO pin

            :param gpioPin:
                The schematic name or number of the pin on the modem

            :return: None
            :rtype: None
            """

            raise NotImplementedError("{} doesn't implement write()!"
                                    .format(self.__class__.__name__))

    def __init__(self) -> None:
        self._gpio = self.GPIO()

    @property
    def gpio(self) -> GPIO:
        """Access the gpio pins of the host
        """

        return self._gpio

    def reset(self) -> None:
        """Reset the modem using the nRESET pin

        Must be driven with an open drain or open collector signal.
        Pull the pin to GND to reset.

        Refer to Skywire Hardware Developers Guide for more information
        """

        raise NotImplementedError("{} doesn't implement reset()!"
                                            .format(self.__class__.__name__))
