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

    class CommError(Exception):
        """An error that occurs when AT communication with a device fails
        """

        pass

    DefaultTimeout = 5.0
    """A default timeout for interacting with a modem"""

    SendNewLine = "\r"
    """The line engins to use to send commands"""

    NewLine = Response.DefaultNewLine
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

        self._logger = logging.getLogger(__name__)

        # Try to make the serial port with our default timeout
        try:
            self._device = serial.Serial(*args, **kwargs, timeout = AtInterface.DefaultTimeout)

        # If it appears the user specified their own timeout, just use that
        except SyntaxError:
            self._device = serial.Serial(*args, **kwargs)

        self._buffer = bytearray()

        # Clear out to begin with
        self._clear()

    def _clear(self):
        """Clears our device's input/output buffers

        :param self:
            Self

        :return none:
        """

        while True:
            self._device.reset_output_buffer()
            self._device.reset_input_buffer()

            if len(self._device.read_all()) < 1:
                break

    @property
    def readTimeout(self):
        """Gets our serial port's read timeout

        :param self:
            Self

        :return Integer:
            Our serial port's read timeout
        """

        return self._device.timeout

    @readTimeout.setter
    def readTimeout(self, timeout):
        """Sets our serial port's read timeout

        :param self:
            Self
        :param timeout:
            The timeout to set

        :return none:
        """

        # Setting the serial port's timeout can cause issues with buffering of
        # input/output, so only set it if necessary
        if self._device.timeout != timeout:
            self._device.timeout = timeout

    @property
    def baudRate(self):
        """Gets our serial port's baud rate

        :param self:
            Self

        :return Integer:
            Our serial port's read timeout
        """

        return self._device.baudrate

    @baudRate.setter
    def baudRate(self, baudRate):
        """Sets our serial port's baud rate

        :param self:
            Self
        :param baudRate:
            The baud rate to use

        :return none:
        """

        self._device.baudrate = baudRate

    @property
    def flowControl(self):
        """Gets our serial port's flow control

        :param self:
            Self

        :return Bool:
            Whether or not RTS/CTS flow control is on
        """

        return self._device.baudrate

    @flowControl.setter
    def flowControl(self, flowControl):
        """Sets our serial port's flow control

        :param self:
            Self
        :param flowControl:
            Whether or not to use RTS/CTS flow control

        :return none:
        """

        self._device.rtscts = flowControl

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

        self.readTimeout = timeout = timeout

        # Allow a zero-second timeout to still potentially read input
        startTime = None

        while True:
            now = time.time()

            # If this is our first time through, note when we started
            if startTime == None:
                startTime = now

            # If we've timed out, stop
            if (now - startTime) > timeout:
                break

            # Get another line of text
            self._buffer.extend(self._device.readline())

            # If the data doesn't actually contain a newline, keep waiting
            #
            # There appear to be issues with readline() that aren't strictly
            # documented, where it's ending and returning a non-empty buffer
            # that *doesn't* contain a newline in it.
            if self._buffer.rfind(b'\n') < 0:
                continue

            # We need to clear our buffer before yielding, as we can't guarantee
            # the caller will re-enter the function again
            buffer = self._buffer

            # We consumed a whole line, so start over
            self._buffer = bytearray()

            self._logger.debug("Read  {}".format(ascii(buffer.decode())))

            # Got another line
            yield buffer.decode()

    def _writeRaw(self, data):
        """Writes raw data

        :param self:
            Self
        :param data:
            The data to write

        :raise CommError:
            Failed to write data

        :return none:
        """

        if self._device.write(data) != len(data):
            raise AtInterface.CommError("Failed to send {}".format(ascii(data.decode())))

        self._logger.debug("Wrote {}".format(ascii(data.decode())))

    def _beginCommand(self, command):
        """Sends a command to the AT interface without expecting a response

        :param command:
            Command to send

        :raise CommError:
            Failed to send command

        :return none:
        """

        # First try to have locked control over the interface by sending the
        # 'AT'
        self._writeRaw("AT".encode())

        # Handle any buffered URCs, which -- since we entered the 'AT' -- we
        # expect to not show up anymore until we're done with the command's full
        # entry and response
        for line in self._getLines(timeout = 0):
            pass

        # Drop the command's 'AT', if any
        if command[:2].upper() == "AT":
            command = command[2:]

        # Drop provided line endings and use our own
        command = command.rstrip(self.NewLine) + self.SendNewLine

        # Write the command
        self._writeRaw(command.encode())

    def _waitForResponse(self, timeout = None):
        """Waits for a certain response

        :param self:
            Self
        :param timeout:
            How long to wait for the response

        :raise CommError:
            Timed out waiting for response

        :return Response:
            The response
        """

        data = ""

        for line in self._getLines(timeout = timeout):
            # Note the additional contents
            data += line

            # Try to get a response from that
            response = Response.makeFromString(string = data, newLine = self.NewLine)

            # If this is a final result, return it
            if response != None:
                return response

        raise AtInterface.CommError("Timeout waiting for response")

    def _filterCommand(self, command, response):
        """Filters out an echoed command from a response

        :param self:
            Self
        :param command:
            The command
        :param response:
            The response

        :return none:
        """

        # Try to filter out the command itself, if present
        commandStart = response.output.find(command)

        # If the command wasn't echoed back, nothing to do
        if commandStart == -1:
            return

        # Skip over the command and the line endings automatically appended
        # after it
        outputStart = commandStart + len(command) + 2

        # If there's also additional line endings due to us manually appending
        # the carriage return, filter that too
        if not command.endswith(self.SendNewLine):
            outputStart += 1

        response.output = response.output[outputStart:]

    def sendCommand(self, command, timeout = None):
        """Sends a command to the AT interface

        :param self:
            Self
        :param command:
            Command to send
        :param timeout:
            How long to wait for the response, if any

        :raise CommError:
            Timed out sending command or waiting for response

        :return Response:
            The response
        """

        # Send the command
        self._beginCommand(command = command)

        # Wait for a response
        response = self._waitForResponse(timeout = timeout)

        # Filter out the command
        self._filterCommand(command = command, response = response)

        return response

    def getUrc(self, pattern = None, timeout = None):
        """Waits for an asynchronous output

        The pattern string can be a regular expression used to filter out
        irrelevant URCs. It must be contained on a single line, as URCs are only
        single lines of text.

        URCs will have their line endings stripped prior to being returned.

        :param self:
            Self
        :param pattern:
            A pattern for filtering URCs
        :param timeout:
            How long to wait for a new URC

        :raise CommError:
            Timed out waiting for URC

        :return String:
            The URC, sans line endings
        """

        # Get another URC
        for line in self._getLines(timeout = timeout):
            # If a pattern was specified but the URC doesn't match, ignore this
            if (pattern != None) and (re.match(pattern, line) == None):
                continue

            # Got a URC that's wanted
            return line.rstrip()

        # We didn't get the URC in time
        raise AtInterface.CommError("Failed to receive URC matching '{}'".format(pattern))

    def getUrcs(self, pattern = None, timeout = None):
        """Waits for multiple asynchronous output

        If a timeout is specified, it will be used for each individual URC as if
        that were the first URC. That is, if a URC is returned and this function
        is re-entered from the yield, the timeout will be measured relative to
        when the function is entered again, *not* from when it was first
        entered.

        :param self:
            Self
        :param pattern:
            A pattern for filtering URCs
        :param timeout:
            How long to wait for a new URC

        :yield String:
            The URC, sans line endings

        :return none:
        """

        while True:
            # Get another URC
            try:
                urc = self.getUrc(pattern = pattern, timeout = timeout)

                yield urc

            # If that failed, we're done
            except AtInterface.CommError:
                break

    def startPrompt(self, *args, **kwargs):
        """Starts a prompt command

        :param self:
            Self
        :param *args:
            Positional arguments
        :param **kwargs:
            Keyword arguments

        :return Prompt:
            The prompt
        """

        return AtInterface.Prompt(self, *args, **kwargs)

    class Prompt:
        """A prompt for sending dynamic data in an AT command
        """

        def __init__(self, interface, dynamic):
            """Creates a new prompt

            :param self:
                Self
            :param interface:
                The AT interface this is on
            :param dynamic:
                Whether or not the incoming data will be dynamic

            :return none:
            """

            self._interface = interface
            self._dynamic = dynamic

            self._command = None

        def __enter__(self):
            """Enters the prompt context

            :param self:
                Self

            :return Prompt:
                Us
            """

            return self

        def __exit__(self, type, value, traceback):
            """Exits the prompt context

            :param self:
                Self
            :param type:
                The type of exception, if any
            :param value:
                The value of the exception, if any
            :param traceback:
                The exception's traceback, if any

            :return none:
            """

            pass

        def startCommand(self, command):
            """Starts a dynamic command

            :param self:
                Self
            :param command:
                The command to send

            :raise CommError:

            :return none:
            """

            # Note the command we're sending so we can try to filter it out of
            # our response later
            self._command = command

            # Send the command
            self._interface._beginCommand(command = command)

        def writeData(self, data):
            """Writes command data

            :param self:
                Self
            :param data:
                The data to write

            :raise CommError:
                Failed to write data

            :return none:
            """

            self._interface._writeRaw(data)

        def finish(self, timeout = None):
            """Finishes the prompt

            :param self:
                Self
            :param timeout:
                How long to wait for the response

            :raise CommError:
                Failed to write data or get response

            :return Response:
                The response
            """

            # If we're a dynamic command, send the terminator
            if self._dynamic:
                self._interface._writeRaw("\x1A".encode())

            # Wait for a response
            response = self._interface._waitForResponse(timeout = timeout)

            # Filter out the command
            if self._command != None:
                self._interface._filterCommand(command = self._command, response = response)

            return response
