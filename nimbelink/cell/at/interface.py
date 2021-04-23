###
 # \file
 #
 # \brief Interfaces with a modem using its AT interface
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import logging
import re
import serial
import time

from nimbelink.cell.at.response import Response

class AtInterface(object):
    """Python class for sending and receiving commands from embedded cellular
    modems
    """

    DefaultTimeout = 5.0
    """A default timeout for interacting with a modem"""

    NewLine = "\r\n"
    """The line endings to expect"""

    def __init__(self, *args, **kwargs):
        """Creates a new AT interface

        :param self:
            Self
        :param *args:
            Arguments to a serial port
        :param **kwargs:
            Keyword arguments to a serial port

        :return none:
        """

        self.logger = logging.getLogger(__name__)

        # Try to make the serial port with our default timeout
        try:
            self.device = serial.Serial(*args, **kwargs, timeout = AtInterface.DefaultTimeout)

        # If it appears the user specified their own timeout, just use that
        except SyntaxError:
            self.device = serial.Serial(*args, **kwargs)

        # Clear out to begin with
        self._clear()

    def _clear(self):
        """Clears our device's input/output buffers

        :param self:
            Self

        :return none:
        """

        while True:
            self.device.reset_output_buffer()
            self.device.reset_input_buffer()

            if len(self.device.read_all()) < 1:
                break

    def _setTimeout(self, timeout):
        """Sets the device's serial port timeout

        :param self:
            Self
        :param timeout:
            The timeout to set

        :return none:
        """

        # Setting the serial port's timeout can cause issues with buffering of
        # input/output, so only set it if necessary
        if self.device.timeout != timeout:
            self.device.timeout = timeout

    def _getLines(self, timeout = None):
        """Gets lines from the device

        Because this function uses 'yield' to return lines, the provided timeout
        will be used for the *entire* handling of lines. In other words, if you
        are given a line while using this function and come back to receive
        another line, the timeout will continue to be relative to when the
        function was first entered, prior to the previous line being returned.

        :param self:
            Self
        :param timeout:
            How long to wait for lines

        :yield String:
            The next line of text

        :return none:
        """

        if timeout == None:
            timeout = AtInterface.DefaultTimeout

        self._setTimeout(timeout = timeout)

        # Allow a zero-second timeout to still potentially read input
        startTime = None

        data = ""

        while True:
            now = time.time()

            # If this is our first time through, note when we started
            if startTime == None:
                startTime = now

            # If we've timed out, stop
            if (now - startTime) > timeout:
                break

            # Get another line of text
            newData = self.device.readline()

            # If we didn't get anything, keep waiting
            if (newData == None) or (len(newData) < 1):
                continue

            # Got another line
            yield newData.decode()

    def _writeRaw(self, data):
        """Writes raw data

        :param self:
            Self
        :param data:
            The data to write

        :return True:
            Data written
        :return False:
            Failed to write data
        """

        if self.device.write(data) != len(data):
            self.logger.error("Failed to write '{}'".format(data))

            return False

        return True

    def _waitForResponse(self, timeout = None):
        """Waits for a certain response

        :param self:
            Self
        :param timeout:
            How long to wait for the response

        :return None:
            Timed out waiting for response
        :return Response:
            The response
        """

        data = ""

        for line in self._getLines(timeout = timeout):
            # Note the additional contents
            data += line

            # Try to get a response from that
            response = Response.makeFromString(string = data)

            # If this is a final result, return it
            if response != None:
                self.logger.info("Receive '{}'".format(response))

                return response

        self.logger.error("Timeout")

        # We must not have gotten a full response
        return None

    def sendCommand(self, command, timeout = None):
        """Sends a command to the AT interface

        :param self:
            Self
        :param command:
            Command to send
        :param timeout:
            How long to wait for the response, if any

        :return None:
            Timed out waiting for response
        :return Response:
            The response
        """

        # If the command doesn't have proper line endings, add them
        if not command.endswith("\r"):
            command += "\r"

        self._clear()

        self.logger.info("Sending '{}'".format(command.rstrip()))

        # Write the command
        if self.device.write(command.encode()) != len(command):
            self.logger.error("Failed to send")

            return None

        # Wait for a response
        response = self._waitForResponse(timeout = timeout)

        # If that failed, just use that
        if response == None:
            return None

        # Try to filter out the command itself, if present
        if (len(response.output) > 0) and (response.output[0] == command.rstrip()):
            response.output.pop(0)

        return response

    def waitUrc(self, urc, timeout = None):
        """Waits for an asynchronous output

        The URC string can be a regular expression, but it must be contained on
        a single line.

        :param self:
            Self
        :param urc:
            The URC to wait for
        :param timeout:
            How long to wait for the URC

        :return None:
            Timed out waiting for URC
        :return String:
            The URC, sans line endings
        """

        for line in self._getLines(timeout = timeout):
            # If the URC matches, great, got it
            if re.match(urc, line) != None:
                return line

        # Must not have gotten our URC
        return None
