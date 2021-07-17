"""
A Skywire Nano modem's application

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import time
import urllib.parse

import nimbelink.cell.modem as modem
import nimbelink.cell.modem.skywire as skywire
import nimbelink.utils as utils

from .dfu import Dfu
from .urcs import Urcs

class App(skywire.App):
    """A Skywire Nano modem's application
    """

    def __init__(self, nano: "SkywireNano") -> None:
        """Creates a new Skywire Nano app

        :param self:
            Self
        :param nano:
            The Skywire Nano we're attached to

        :return none:
        """

        super().__init__(apps = [
            skywire.App.Instance(id = 0, name = "stack"),
            skywire.App.Instance(id = 1, name = "at"),
            skywire.App.Instance(id = 2, name = "modem")
        ])

        self._nano = nano

    def _getVersion(self, app: skywire.App.Instance) -> str:
        """Gets an application's version

        :param self:
            Self
        :param app:
            The application whose version to get

        :raise AtError:
            Failed to get versions

        :return str:
            The application's version
        """

        # Get the stack and AT interface versions
        response = self._nano.at.sendCommand("AT#APPVER?")

        # If that failed, that's a paddlin'
        if not response:
            raise modem.AtError(response)

        versions = {}

        # Parse the versions
        for line in response.lines:
            # Split the string into its prefix, image ID, and version
            fields = line.split(":")

            # If that failed, that's a paddlin'
            if len(fields) != 3:
                raise modem.AtError(response, "Invalid app version response")

            # Make sure we remove any whitespace
            versions[fields[1].strip()] = fields[2].strip()

        # If there aren't two versions, that's a paddlin'
        if len(versions) != 2:
            raise modem.AtError(response, "Failed to get all app versions")

        # Get the modem/co-processor version
        response = self._nano.at.sendCommand("AT+CGMR")

        # If that failed, that's a paddlin'
        if not response:
            raise modem.AtError(response)

        lines = response.lines

        # If there isn't a single version, that's a paddlin'
        if len(lines[0]) < 1:
            raise modem.AtError(response, "Invalid co-processor version response")

        # The modem version is just a single string, so add our own identifier
        # for it
        versions["MFW"] = lines[0]

        if (app.name == "stack") and ("NLS" in versions):
            return versions["NLS"]

        if (app.name == "at") and ("ATI" in versions):
            return versions["ATI"]

        if (app.name == "modem") and ("MFW" in versions):
            return versions["MFW"]

        raise KeyError(f"Version for {app.name} not available")

    def _startDfu(self, reboot: bool = None) -> None:
        """Starts a DFU process

        :param self:
            Self
        :param reboot:
            Whether or not to permit rebooting when done

        :raise modem.AtError:
            Failed to start DFU

        :return none:
        """

        if reboot is None:
            reboot = True

        # If we have an AT interface, use it
        if self._nano.at is not None:
            # Make our command
            command = "AT#FWUPD=1"

            # If we're not rebooting, prevent it
            if not reboot:
                command += ",0"

            # Kick off the DFU
            response = self._nano.at.sendCommand(command)

            # If that failed, that's a paddlin'
            if not response:
                raise modem.AtError(response)

        # Else, if we have a debug tool, use it
        elif self._nano.tool is not None:
            if not self._nano.tool.mailbox.dfu(autoReboot = reboot):
                raise modem.AtError("Failed to trigger DFU with debugger and no AT interface")

        # Else, no way to do this
        else:
            raise modem.AtError("No debugger nor AT interface to trigger DFU")

        # Try to give the logging a little time to come across before we start
        # using the serial port
        time.sleep(1.0)

    def _waitForDfuFinish(self, reboot: bool) -> None:
        """Waits for a DFU to finish, including any reboot

        :param self:
            Self
        :param reboot:
            Whether or not a reboot is expected

        :raise OSError:
            DFU failed

        :return none:
        """

        applying = False

        # Wait for a final DFU URC
        #
        # URCs should come somewhat readily until it's being applied, but we'll
        # be a little flexible to handle poorer network connections.
        for urc in self._nano.at.getUrcs(pattern = "DFU: ", timeout = 30):
            # Parse the DFU URC
            dfu = Urcs.Dfu.makeFromString(string = urc)

            # If this is a failure, that's a paddlin'
            if dfu.type == Urcs.Dfu.Type.Failure:
                raise OSError(f"DFU failed ({urc})")

            # If this is an indication of DFU finishing, we must not need to
            # wait for the reboot
            if dfu.type == Urcs.Dfu.Type.Done:
                return

            # If this is an indication of DFU starting to apply
            if dfu.type == Urcs.Dfu.Type.Applying:
                # If we're not planning on rebooting, we're done
                if not reboot:
                    return

                # Move on
                applying = True

                break

        # Wait for the device to boot again
        #
        # The boot loader will potentially be applying both images, which can
        # take quite a while, so give it plenty of time.
        self._nano.waitForBoot(timeout = 120)

        # We'll need at least one complete update
        count = 0

        # The done URCs should come quickly once they come at all, so don't wait
        # around too much more
        #
        # We can't know for sure how many pending updates there are, so we
        # should spend some time trying to collect any and all DFU URCs to make
        # sure there weren't any failures.
        for urc in self._nano.at.getUrcs(pattern = "DFU: ", timeout = 2):
            # Parse the DFU URC
            dfu = Urcs.Dfu.makeFromString(string = urc)

            # If this DFU finished, count it
            if dfu.type == Urcs.Dfu.Type.Done:
                count += 1

            # Else, if this is a failure, that's a paddlin'
            elif dfu.type == Urcs.Dfu.Type.Failure:
                raise OSError(f"DFU failed ({urc})")

            # Else, this is an unexpected DFU URC, so that's a paddlin'
            else:
                raise modem.AtError(urc, "Unexpected DFU URC")

        # If we failed to see any successful final URCs, that's a paddlin'
        if count < 1:
            raise modem.AtError(None, "Failed to get final DFU URC")

    def upload(self, data: bytearray, type: Dfu.Type, reboot: bool = None) -> None:
        """Uploads DFU data to the Skywire Nano

        :param self:
            Self
        :param data:
            The data to upload
        :param type:
            The type of data to upload
        :param reboot:
            Whether or not to permit rebooting

        :raise AtError:
            Failed to start upload
        :raise OSError:
            Failed to send data

        :return none:
        """

        if reboot is None:
            reboot = True

        # If we don't have a kernel log serial port to use, we won't be able
        # to facilitate this
        if self._nano.kernelLog is None:
            raise OSError("Cannot upload without kernel logging serial port")

        # Format the data for DFU
        data = Dfu.format(data = data, type = type)

        # Trigger XMODEM DFU
        self._startDfu(reboot = reboot)

        # Make an XMODEM protocol to use to send the data
        xmodem = utils.Xmodem(device = self._nano.kernelLog)

        # If we would use the larger packet size but it would only result in a
        # single packet being sent for the whole transfer, make sure we force
        # using the 128-byte transfer packet size
        #
        # This is per a bug in the Skywire Nano.
        if (xmodem.packetSize == 1024) and (len(data) <= 1024):
            xmodem.packetSize = 128

        # Send the data
        transferred = xmodem.transfer(data = data)

        # If that failed, that's a paddlin'
        if not transferred:
            raise OSError("Failed to send update data")

        # If this isn't a DFU type that needs a reboot or we aren't allowing
        # reboots, nothing left to do
        if not Dfu.needsReboot(type = type) or not reboot:
            return

        # If there isn't an AT interface, still allow the upload to succeed, but
        # warn about not being able to wait for the finishing indication
        if self._nano.at is None:
            self._nano._logger.warning("No AT interface, cannot wait for DFU to complete")

            return

        # Wait for DFU to finish
        self._waitForDfuFinish(reboot = reboot)

    def fota(self, url: str = None, reboot: bool = None) -> None:
        """Updates an application on the Skywire Nano

        :param self:
            Self
        :param url:
            A URL for an update file to use
        :param file:
            A local file to send to the device
        :param reboot:
            Whether or not to reboot after the update completes

        :raise OSError:
            Cannot perform update without kernel logging serial port
        :raise OSError:
            Failed to send update data
        :raise AtError:
            Failed to start update

        :return none:
        """

        if reboot is None:
            reboot = True

        # Split the URL into a hostname and a filename
        result = urllib.parse.urlparse(url)

        # Make our command
        #
        # Note that the path from urllib will contain any forward slash between
        # it and the network location, which we'll want to omit from our AT
        # command.
        command = f"AT#XFOTA=\"{result.netloc}\",\"{result.path[1:]}\""

        # If we're not rebooting, prevent it
        if not reboot:
            command += ",,0"

        # Kick off the FOTA
        response = self._nano.at.sendCommand(command)

        # If that failed, that's a paddlin'
        if not response:
            raise modem.AtError(response)

        self._waitForDfuFinish(reboot = reboot)
