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

    def update(self, url: str = None, file: str = None, reboot: bool = True) -> None:
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

        # If we're sending a file
        if file != None:
            # If we don't have a kernel log serial port to use, we won't be able
            # to facilitate this
            if self._nano.kernelLog == None:
                raise OSError("Cannot perform update without kernel logging serial port")

            # Open the file before trying to start the update, as we don't want
            # to have DFU waiting for us if we're just going to fail to open the
            # file anyway
            with open(file, "rb") as _file:
                # Make an XMODEM protocol to use to send the data
                xmodem = utils.Xmodem(device = self._nano.kernelLog)

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

                # Try to give the logging a little time to come across before we
                # start using the serial port
                time.sleep(0.5)

                # Send the data
                transferred = xmodem.transfer(data = _file.read())

                # If that failed, that's a paddlin'
                if not transferred:
                    raise OSError("Failed to send update data")

        # Else, if we're using FOTA
        elif url != None:
            # Split the URL into a hostname and a filename
            result = urllib.parse.urlparse(url)

            # Make our command
            #
            # Note that the path from urllib will contain any forward slash
            # between it and the network location, which we'll want to omit from
            # our AT command.
            command = f"AT#XFOTA=\"{result.netloc}\",\"{result.path[1:]}\""

            # If we're not rebooting, prevent it
            if not reboot:
                command += ",,0"

            # Kick off the FOTA
            response = self._nano.at.sendCommand(command)

            # If that failed, that's a paddlin'
            if not response:
                raise modem.AtError(response)

        # Else, that's a paddlin'
        else:
            raise ValueError("Must have either a URL or a file for updating")

        applying = False

        # Wait for a final DFU URC
        #
        # URCs should come somewhat readily until it's being applied, but we'll
        # be a little flexible to handle poorer network connections.
        for urc in self._nano.at.getUrcs(pattern = "DFU: ", timeout = 30):
            # Parse the DFU URC
            dfu = Urcs.Dfu.makeFromString(string = urc)

            # If this is an indication of DFU finishing, we don't expect it yet,
            # so that's a paddlin'
            if dfu.type == Urcs.Dfu.Type.Done:
                raise modem.AtError(urc, "Premature DFU finish")

            # Else, if this is an indication of DFU starting to apply
            elif dfu.type == Urcs.Dfu.Type.Applying:
                # If we're not planning on rebooting, we're done
                if not reboot:
                    return

                # Move on
                applying = True

                break

            # Else, if this is a failure, that's a paddlin'
            elif dfu.type == Urcs.Dfu.Type.Failure:
                raise OSError(f"DFU failed ({urc})")

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
