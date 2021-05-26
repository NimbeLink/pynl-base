"""
A Skywire Nano modem

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import serial

import nimbelink.cell.at as at
import nimbelink.cell.modem as modem
import nimbelink.cell.modem.skywire as skywire

from nimbelink.cell.modem.nano.app import App
from nimbelink.cell.modem.nano.gpio import Gpio
from nimbelink.cell.modem.nano.sim import Sim
from nimbelink.cell.modem.nano.socket import Socket

class SkywireNano(skywire.Skywire):
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

        # The host of the Nano
        self._host = None

        self._app = App(self)
        self._gpio = Gpio(self)
        self._sim = Sim(self)
        self._socket = Socket(self)

        self._kernelLogDevice = kernelLogDevice

    @property
    def host(self):
        """Gets our host

        :param self:
            Self

        :return: The host for the Nano
        :rtype: Host
        """

        return self._host

    @host.setter
    def host(self, newHost):
        """Sets our host

        :param self:
            Self

        :return: None
        :rtype: None
        """

        self._host = newHost

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

        :raise AtError:
            Failed to detect device's boot

        :return none:
        """

        # The boot loader generally doesn't take long, so give it a reasonable
        # amount of time
        if timeout is None:
            timeout = 5

        try:
            self.at.getUrc(pattern = r".*READY", timeout = timeout)

        except at.Interface.CommError:
            raise modem.AtError(None, "Failed to detect boot")

    def reboot(self) -> None:
        """Gracefully reboot the modem

        :param self:
            Self

        :raise AtError:
            Failed to either send reboot command or get +RESET URC

        :return: None
        :rtype: None
        """

        # Tell the modem to reboot
        try:
            self.at.sendCommand("AT#REBOOT")
        except at.Interface.CommError:
            raise modem.AtError(None, "Failed to issue reboot command")

        # Wait for the +RESET URC
        try:
            self.at.getUrc(pattern = r"\+RESET")
        except at.Interface.CommError:
            raise modem.AtError(None, "Failed to get +RESET URC")

    def shutdown(self) -> None:
        """Gracefully shut down the modem

        :param self:
            Self

        :raise AtError:
            Failed to send shutdown command or get +SHUTDOWN URC

        :return: None
        :rtype: None
        """

        # Tell the modem to shutdown
        try:
            self.at.sendCommand("AT#SHUTDOWN")
        except at.Interface.CommError:
            raise modem.AtError(None, "Failed to issue shutdown command")

        # Wait for the +SHUTDOWN URC
        try:
            self.at.getUrc(pattern = r"\+SHUTDOWN")
        except at.Interface.CommError:
            raise modem.AtError(None, "Failed to get +SHUTDOWN URC")

    @property
    def kernel(self) -> serial.Serial:
        """Gets the kernel logging device

        :param self:
            Self

        :return:
            The device connected to the modem's kernel log
        :rtype: serial.Serial
        """

        return self._kernelLogDevice

    def enterSerialBootloaderRecovery(self) -> None:
        """Reset the modem and have it enter the serial bootloader recovery
        """

        # Pull IO5 High in order to enter recovery on next boot
        self.host.gpio.write("IO5", True)

        # Shut down the modem safely
        # Note: We must do a shutdown, then a reset. A reboot doesn't seem to
        # be reliable
        self.shutdown()

        # Reset the modem
        self.reset()

    def exitSerialBootloaderRecovery(self) -> None:
        """Exit serial bootloader recovery and have the modem start normally
        """

        # Pull IO5 to GND
        self.host.gpio.write("IO5", False)

        # Reset modem in order to leave serial bootloader recovery
        self.reset()

        # Wait for the device to boot, since we are probably doing a DFU,
        # this may take longer than a normal boot
        self.waitForBoot(60)
