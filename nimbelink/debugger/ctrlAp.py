"""
Provides handling of actions using a DAP's AHB-AP interface

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import time
import typing

from .dap import Dap

class CtrlAp:
    """A Debug Access Port
    """

    Port = 4
    """The access port we use"""

    class Registers:
        """The nRF9160 CTRL-AP register set
        """

        Reset                   = 0x000
        EraseAll                = 0x004
        EraseAllStatus          = 0x008
        ApProtectStatus         = 0x00C
        EraseProtectStatus      = 0x018
        EraseProtectDisable     = 0x01C
        MailboxTxData           = 0x020
        MailboxTxStatus         = 0x024
        MailboxRxData           = 0x028
        MailboxRxStatus         = 0x02C
        Idr                     = 0x0FC

    def __init__(self, dap: Dap) -> None:
        """Creates a new AHB-AP

        :param self:
            Self
        :param dap:
            The DAP to use

        :return none:
        """

        self._dap = dap

    def readRegister(self, register: int) -> int:
        """Reads a register value

        :param self:
            Self
        :param register:
            The register to read

        :return Integer:
            The register's value
        """

        return self._dap.api.read_access_port_register(self.Port, register)

    def _waitAllErased(self) -> bool:
        """Waits for an erase all operation to finish

        :param self:
            Self

        :return True:
            All erased
        :return False:
            Failed to erase all
        """

        # Erase can sometimes take a while, so give this a super duper long
        # while
        for i in range(30):
            # Get the erase status
            status = self.readRegister(self.Registers.EraseAllStatus)

            # If the erase isn't shown as happening on the first go-round, then
            # we probably failed to kick it off
            if (i == 0) and (status != 1):
                return False

            # If the erase is now done, we're done
            if status == 0:
                return True

            # Keep waiting for the erase to finish
            time.sleep(1)

        # Apparently we didn't see the end of the erase
        return False

    def eraseAll(self) -> bool:
        """Attempts to perform a mass erase

        :param self:
            Self

        :return True:
            All erased
        :return False:
            Failed to erase all
        """

        self._dap.api.write_access_port_register(self.Port, self.Registers.EraseAll, 0x1)

        # Make sure the value gets flushed
        self.readRegister(self.Registers.Reset)

        return self._waitAllErased()

    def disableEraseProtect(self, key: int) -> bool:
        """Attempts to disable erase protection

        :param self:
            Self
        :param key:
            The 32-bit key to use

        :return True:
            Erase protection disabled
        :return False:
            Failed to disable erase protection
        """

        self._dap.api.write_access_port_register(self.Port, self.Registers.EraseProtectDisable, key)

        # Make sure the value gets flushed
        self.readRegister(self.Registers.Reset)

        return self._waitAllErased()

    def waitMailboxRead(self, timeout: float = None) -> bool:
        """Waits for our debugger->CPU data to be read by the CPU

        :param self:
            Self
        :param timeout:
            How long to wait, in seconds

        :return True:
            Mailbox data read by CPU
        :return False:
            Timed out before mailbox data read by CPU
        """

        start = time.time()

        while True:
            # Get the TX status
            status = self.readRegister(self.Registers.MailboxTxStatus)

            # If it's been read, we're done
            if status == 0:
                return True

            # If they specified a timeout and it's been too long, move on
            if (timeout is not None) and ((time.time() - start) >= timeout):
                return False

    def writeMailbox(self, values: typing.List[int], flush: bool = False, timeout: float = 2.0) -> bool:
        """Writes debugger->CPU values to the CTRL-AP mailbox

        :param self:
            Self
        :param values:
            The values to write, as words
        :param flush:
            Whether or not to flush the final write
        :param timeout:
            How long to try writing for

        :return True:
            Values sent
        :return False:
            Failed to send values
        """

        start = time.time()

        for value in values:
            now = time.time()

            # If it's been too long, move on
            if (now - start) >= timeout:
                return False

            # Write out the next value
            self._dap.api.write_access_port_register(self.Port, self.Registers.MailboxTxData, value)

            # Wait for the value to be read
            if not self.waitMailboxRead(timeout = timeout):
                return False

            # Note how much time we have used up
            timeout -= (now - start)

        # If we should, make sure the final value gets flushed
        if flush:
            self.readRegister(self.Registers.Reset)

            # Wait for the value to be read
            if not self.waitMailboxRead(timeout = timeout):
                return False

        return True

    def waitMailboxWritten(self, timeout: float) -> bool:
        """Waits for our mailbox to have CPU->debugger data

        :param self:
            Self
        :param timeout:
            How long to wait, in seconds

        :return True:
            Mailbox data from CPU available
        :return False:
            Timed out before mailbox data from CPU available
        """

        start = time.time()

        while True:
            # Get the RX status
            status = self.readRegister(self.Registers.MailboxRxStatus)

            # If it's been written to, we're done
            if status != 0:
                return True

            # If they specified a timeout and it's been too long, move on
            if (timeout is not None) and ((time.time() - start) >= timeout):
                return False

    def readMailbox(self, length: int = 1, timeout: float = 2.0) -> typing.List[int]:
        """Reads CPU->debugger values from the CTRL-AP mailbox

        :param self:
            Self
        :param length:
            The amount of data to read
        :param timeout:
            How long to try reading for

        :return None:
            Failed to read data
        :return Array of integers:
            The read values
        """

        values = []

        start = time.time()

        for i in range(length):
            # Wait for a value to be written
            if not self.waitMailboxWritten(timeout = timeout):
                return None

            now = time.time()

            # If it's been too long, move on
            if (now - start) >= timeout:
                return None

            # Note how much time we have used up
            timeout -= (now - start)

            # Get the next value
            value = self.readRegister(self.Registers.MailboxRxData)

            values.append(value)

        return values

    def clearTx(self) -> None:
        """Clears the debugger->CPU mailbox buffering

        :param self:
            Self

        :return none:
        """

        # If the CPU hasn't read our debugger->CPU data, do it for it
        if not self.waitMailboxRead(timeout = 0.0):
            self.readRegister(self.Registers.MailboxTxData)

    def clearRx(self) -> None:
        """Clears the CPU->debugger mailbox buffering

        :param self:
            Self

        :return none:
        """

        # Make sure all of our outgoing stuff is flushed
        self.readRegister(self.Registers.Reset)

        # If there's more CPU->debugger data, keep reading that
        while self.readMailbox(timeout = 0.0) is not None:
            pass

    def clear(self) -> None:
        """Clears the CPU->debugger mailbox buffering

        :param self:
            Self

        :return none:
        """

        self.clearTx()
        self.clearRx()
