###
 # \file
 #
 # \brief A Skywire Nano modem
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

from nimbelink.cell.at.interface import AtInterface
from nimbelink.cell.modem.skywire import Skywire

from nimbelink.cell.modem.nano.app import App
from nimbelink.cell.modem.nano.gpio import Gpio
from nimbelink.cell.modem.nano.sim import Sim
from nimbelink.cell.modem.nano.socket import Socket

class SkywireNano(Skywire):
    """A Skywire modem
    """

    def __init__(self, *args, kernelLogDevice = None, **kwargs):
        """Creates a new Skywire Nano modem

        :param self:
            Self
        :param *args:
            Positional arguments
        :param **kwargs:
            Keyword arguments
        :param kernelLogDevice:
            A serial port for our kernel logging output

        :return none:
        """

        super(SkywireNano, self).__init__(*args, **kwargs)

        self._app = App(self)
        self._gpio = Gpio(self)
        self._sim = Sim(self)
        self._socket = Socket(self)

        self._kernelLogDevice = kernelLogDevice

    @property
    def app(self):
        """Gets our app

        :param self:
            Self

        :return App:
            Our app
        """

        return self._app

    @property
    def gpio(self):
        """Gets our GPIOs

        :param self:
            Self

        :return Gpio:
            Our GPIOs
        """

        return self._gpio

    @property
    def sim(self):
        """Gets our SIM

        :param self:
            Self

        :return Sim:
            Our SIM
        """

        return self._sim

    @property
    def socket(self):
        """Gets our socket

        :param self:
            Self

        :return Socket:
            Our socket
        """

        return self._socket

    def waitForBoot(self, timeout = None):
        """Waits for the Skywire Nano to boot

        :param self:
            Self
        :param timeout:
            How long to wait

        :raise Skywire.AtError:
            Failed to detect device's boot

        :return none:
        """

        # The boot loader generally doesn't take long, so give it a reasonable
        # amount of time
        if timeout == None:
            timeout = 5

        try:
            self.at.getUrc("READY", timeout = timeout)

        except AtInterface.CommError:
            raise Skywire.AtError(None, "Failed to detect boot")
