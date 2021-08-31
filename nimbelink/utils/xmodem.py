"""
Sends data using an XMODEM interface

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import logging
import serial
import time
import typing

class Xmodem:
    """An XMODEM interface
    """

    ChunkSize = 256
    """How much we'll chunk transmission data into"""

    class Packet:
        """An XMODEM packet
        """

        TransferSizes = [128, 1024]
        """The available packet sizes"""

        SmallStart = 0x01
        """A start-of-header byte value for small packets"""

        LargeStart = 0x02
        """A start-of-header byte value for large packets"""

        EndOfTransmission = 0x04
        """An end of transmission byte value"""

        Ack = 0x06
        """A packet acknowledgement byte value"""

        Nak = 0x15
        """A packet no-acknowledgement bytes value"""

        Cancelled = 0x18
        """A cancellation of transmission byte value"""

        Responses = [
            Ack,
            Nak,
        ]
        """Our valid response values"""

        @classmethod
        def getInversePacketId(cls, packetId: int) -> int:
            """Gets the 'inverse' packet ID

            :param cls:
                Class
            :param packetId:
                The packet ID to get the inverse of

            :return inversePacketId:
                The inverse packet ID
            """

            return (255 - packetId) & 0xFF

        @classmethod
        def getPacket(cls, packetData: bytearray, packetId: int) -> bytearray:
            """Gets an XMODEM packet from data and an ID

            :param cls:
                Class
            :param packetData:
                The data to packetize
            :param packetId:
                The ID of this packet

            :raise ValueError:
                Packet data too large

            :return Array of bytes:
                The packet
            """

            padLength = 0

            if len(packetData) <= 128:
                packetStart = cls.SmallStart
                padLength = 128 - len(packetData)
            elif len(packetData) <= 1024:
                packetStart = cls.LargeStart
                padLength = 1024 - len(packetData)
            else:
                raise ValueError("Cannot send data that doesn't fit into 128- or 1024-byte packet")

            # If we need to pad the packet, do so
            #
            # Original protocol uses 0x1a as the padding character, but 0xff was
            # done for the Skywire Nano.
            padCharacter = 0xff

            if padLength > 0:
                packetData += bytearray([padCharacter] * padLength)

            # Figure out the next packet's ID, making sure we always stay a byte
            inversePacketId = cls.getInversePacketId(packetId = packetId)

            # Compile the header and footer
            packetHeader = bytearray([packetStart, packetId, inversePacketId])

            # Checksum always starts at 0
            checksum = 0

            # Add together each byte, making sure we always stay a byte
            for byte in packetData:
                checksum = (checksum + byte) & 0xFF

            packetFooter = bytearray([checksum])

            # Compile the full packet
            return packetHeader + packetData + packetFooter

        @classmethod
        def getFirstPacketId(cls) -> int:
            """Gets the first packet ID in the sequence

            :param cls:
                Class

            :return 0x01:
                Always
            """

            return 0x01

        @classmethod
        def getNextPacketId(cls, packetId: int) -> int:
            """Gets the next packet ID in the sequence

            :param cls:
                Class
            :param packetId:
                The current packet ID

            :return Byte:
                The next packet ID
            """

            return (packetId + 1) & 0xFF

    def __init__(self, device: serial.Serial) -> None:
        """Creates a new XMODEM interface

        :param self:
            Self
        :param device:
            Our UART device

        :return none:
        """

        # Get a reference to the logger for this class
        self._logger = logging.getLogger(__name__)

        # The serial device we are transfering a file over
        self._device = device

        # The id of the current packet being sent
        self._packetId = Xmodem.Packet.getFirstPacketId()

        # Default to packet sizes of 1024
        self.packetSize = 1024

        # Set some default XMODEM timeouts
        self.startTimeout = 30.0
        self.stopTimeout = 30.0
        self.packetTimeout = 2.0

    def _logData(self, data: bytearray, output: bool) -> None:
        """Logs data

        :param self:
            Self
        :param data:
            The data to log
        :param output:
            Whether this is outbound or inbound data

        :return none:
        """

        if output:
            self._logger.debug(">>> %s", ascii(data))

        else:
            self._logger.debug("<<< %s", ascii(data))

    def _clear(self) -> None:
        """Clears our device's input/output buffers

        :param self:
            Self

        :return none:
        """

        while len(self._device.read_all()) > 0:
            self._device.reset_output_buffer()
            self._device.reset_input_buffer()

    def _sendData(self, data: bytearray) -> bool:
        """Sends XMODEM data

        :param self:
            Self
        :param data:
            The data to send

        :return True:
            Data sent
        :return False:
            Failed to send data
        """

        # Note how much data we have to send
        dataLength = len(data)

        # If we aren't using flow control, chunk the data
        if not self._device.rtscts:
            self._logger.debug("No flow control, chunking data")

            writeLength = 0

            while True:
                # If we're out of data to chunk, move on
                if len(data) < 1:
                    break

                # Get our next chunk
                nextData = data[0:Xmodem.ChunkSize]

                # Drop the data we are sending
                data = data[Xmodem.ChunkSize:]

                # Log the data
                self._logData(data = nextData, output = True)

                # Wait a bit for the device to handle any previous
                # operations/data
                time.sleep(0.1)

                # Write the next chunk
                writeLength += self._device.write(nextData)

        # Else, just spit everything out
        else:
            # Log the data
            self._logData(data = data, output = True)

            writeLength = self._device.write(data)

        # If that failed, that's a paddlin'
        if writeLength != dataLength:
            self._logger.error("Failed to send all bytes (%d/%d)", writeLength, dataLength)

            return False

        # Data sent successfully
        return True

    def _getResponse(self, timeout: float, dropGarbage: bool = False) -> typing.Union[int, None]:
        """Gets a single-byte XMODEM response

        :param self:
            Self
        :param timeout:
            How long to wait for the response
        :param dropGarbage:
            Whether or not to gracefully drop garbage and keep waiting

        :return int:
            The response byte
        :return None:
            Failed to get a response
        """

        # If we have one, update the read timeout so we wait the proper amount
        # of time for a packet response
        if timeout is not None:
            self._device.timeout = timeout

        # We'll also manually keep track of time to avoid issues with the
        # pyserial timeout handling
        start = time.time()

        while True:
            # If we've got a time limit and we've gone over, abort
            if (timeout is not None) and ((time.time() - start) >= timeout):
                self._logger.error("Failed to get response")

                return None

            # Try reading another byte
            response = self._device.read(1)

            # If that failed, keep waiting
            if (response is None) or (len(response) < 1):
                continue

            # Log the response
            self._logData(data = response, output = False)

            # If this is a valid response, use it
            if response[0] in Xmodem.Packet.Responses:
                return response[0]

            # If we are allowed to gracefully drop garbage, do so and keep
            # waiting for a proper response
            if dropGarbage:
                self._logger.debug("Got invalid response value, trying again")

                continue

            self._logger.warning("Got invalid response value, assuming transmission aborted early")

            # We didn't get a valid response, but we're not allowed to
            # gracefully drop it, so use it
            return response[0]

    def _startTransmission(self) -> bool:
        """Starts XMODEM transmission

        :param self:
            Self

        :return True:
            Transmission started
        :return False:
            Failed to start transmission
        """

        # Initialize our packet ID
        self._packetId = Xmodem.Packet.getFirstPacketId()

        # Try to get our initial NAK
        #
        # Allow dropping garbage in case any logging is left over from before
        # XMODEM kicked off.
        response = self._getResponse(timeout = self.startTimeout, dropGarbage = True)

        # If we got it, great
        if response == Xmodem.Packet.Nak:
            self._logger.info("Transfer started")

            return True

        self._logger.error("Failed to get starting NAK")

        return False

    def _endTransmission(self) -> bool:
        """Ends XMODEM transmission

        :param self:
            Self

        :return True:
            Transmission ended successfully
        :return False:
            Ending transmission failed
        """

        # Send our indication of transmission ending
        sent = self._sendData(bytearray([Xmodem.Packet.EndOfTransmission]))

        # If that failed, abort
        if not sent:
            self._logger.error("Failed to send end of transmission")

            return False

        # Try to get our final ACK/NAK
        response = self._getResponse(timeout = self.stopTimeout)

        # If we got an ACK, great
        if response == Xmodem.Packet.Ack:
            self._logger.info("End of transfer ACKed")

            return True

        # If we got a NAK, still call it a success, but warn about it
        #
        # Some products have a bug where a NAK is erroneously sent on the final
        # EOT indication.
        if response == Xmodem.Packet.Nak:
            self._logger.warning("End of transfer NAKed")

            return True

        # Failed to get ending ACK
        self._logger.error("Failed to get final ACK")

        return False

    def _sendPacket(self, packetData: bytearray) -> int:
        """Sends a packet to a device

        :param self:
            Self
        :param packetData:
            The data to send

        :return True:
            Packet sent and acknowledged
        :return False:
            Failed to send packet
        """

        while True:
            # Get the packet
            packet = Xmodem.Packet.getPacket(
                packetData = packetData,
                packetId = self._packetId
            )

            # Send the next packet of data
            sent = self._sendData(data = Xmodem.Packet.getPacket(
                packetData = packetData,
                packetId = self._packetId
            ))

            # If that failed, that's a paddlin'
            if not sent:
                self._logger.error("Failed to send next packet")

                return False

            # Wait for a response
            response = self._getResponse(timeout = self.packetTimeout)

            # If the modem ACKed the packet, move on
            if response == Xmodem.Packet.Ack:
                # Use the next packet ID next time
                self._packetId = Xmodem.Packet.getNextPacketId(packetId = self._packetId)

                return True

            # If the modem NAKed the packet, try again
            if response == Xmodem.Packet.Nak:
                self._logger.warning("Packet NAKed, retrying")

                continue

            # We must have gotten a garbage response, so abort
            self._logger.warning("Failed to get ACK")

            return False

    def transfer(self, data: bytearray) -> bool:
        """Transfers data using XMODEM

        :param self:
            Self
        :param data:
            Bytes-like data to send

        :raise ValueError:
            Invalid packet size

        :return True
            File sent
        :return False
            Failed to send file
        """

        # Result of transfer is failure until proven otherwise
        success = False

        # Number of bytes from data that we have sent to the modem
        count = 0

        # Clear out any previous data in the serial buffers
        self._clear()

        # If we fail to kick off transmission, that's a paddlin'
        if not self._startTransmission():
            return False

        self._logger.info("Sending %d bytes", len(data))

        # Try sending the data to the modem
        while True:
            # Delay a little bit to help with stability
            time.sleep(0.01)

            # Try to read the next chunk of data
            packetData = data[count : count + self.packetSize]

            # If we're out of data, move on
            if len(packetData) < 1:
                success = True
                break

            self._logger.info("Sending bytes %d-%d", count, count + self.packetSize)

            # If we fail to send the data, stop
            if not self._sendPacket(packetData = packetData):
                break

            # Use the next chunk of data
            count += len(packetData)

        self._logger.info("Ending transfer...")

        # Let the device know we're done
        if not self._endTransmission():
            success = False

        if success:
            self._logger.info("Transfer done!")

        return success
