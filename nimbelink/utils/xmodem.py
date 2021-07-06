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
        self.packetTimeout = None

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

        # Clear out any previous data in the serial buffers
        self._clear()

        beginTime = time.time()

        # Try for 30 seconds to get the starting NAK, discarding single bytes
        # until we timeout or get a NAK
        while (time.time() - beginTime) < self.startTimeout:
            # Try reading a single byte from the serial device
            start = self._device.read(1)

            # Make sure we didn't timeout
            if start:
                # Log the byte
                self._logData(data = start, output = False)

                # If we got a NAK return success
                if start[0] == Xmodem.Packet.Nak:
                    return True

        # Failed to get starting NAK
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

        stopData = bytearray([Xmodem.Packet.EndOfTransmission])

        self._logData(data = stopData, output = True)

        # Stop transmission
        self._device.write(stopData)

        beginTime = time.time()

        # Try for 30 seconds to get the last NAK, discarding single bytes until
        # we timeout or get a NAK
        while (time.time() - beginTime) < self.stopTimeout:
            # Try reading a single byte from the serial device
            start = self._device.read(1)

            # Make sure we didn't timeout
            if start:
                # Log the byte
                self._logData(data = start, output = False)

                # If we got an ACK return success
                if start[0] == Xmodem.Packet.Ack:
                    return True

                # If we got a NAK, still return success, but warn about it
                #
                # Some products have a bug where a NAK is erroneously sent on
                # the final EOT indication.
                if start[0] == Xmodem.Packet.Nak:
                    self._logger.warning("EOT response was a NAK")

                    return True

        # Failed to get ending ACK
        self._logger.error("Failed to get final ACK")

        return False

    def _sendData(self, packetData: bytearray) -> int:
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

        # If we have one, update the read timeout so we wait the proper amount
        # of time for a packet response
        if self.packetTimeout is not None:
            self._device.timeout = self.packetTimeout

        while True:
            # Get the packet
            packet = Xmodem.Packet.getPacket(
                packetData = packetData,
                packetId = self._packetId
            )

            self._logData(data = packet, output = True)

            # If we aren't using flow control, chunk the data
            if not self._device.rtscts:
                writeLength = 0

                packetBytes = list(packet)

                while True:
                    if len(packetBytes) < 1:
                        break

                    time.sleep(0.1)

                    writeLength += self._device.write(packetBytes[0:Xmodem.ChunkSize])

                    packetBytes = packetBytes[Xmodem.ChunkSize:]

            # Else, just spit everything out
            else:
                writeLength = self._device.write(packet)

            # If that failed, that's a paddlin'
            if writeLength != len(packet):
                self._logger.error("Failed to send all bytes (%d/%d)", writeLength, len(packet))

                return False

            # Wait for a response
            response = self._device.read(1)

            # If that failed, that's a paddlin'
            if (response is None) or (len(response) < 1):
                self._logger.error("Failed to get response")

                return False

            self._logData(data = response, output = False)

            # If the modem ACKed the packet, move on
            if response[0] == Xmodem.Packet.Ack:
                # Use the next packet ID next time
                self._packetId = Xmodem.Packet.getNextPacketId(packetId = self._packetId)

                return True

            # If the modem NAKed the packet, try again
            if response[0] == Xmodem.Packet.Nak:
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

            self._logger.debug("Sending bytes %d-%d", count, count + self.packetSize)

            # If we fail to send the data, stop
            if not self._sendData(packetData = packetData):
                break

            # Use the next chunk of data
            count += len(packetData)

        if success:
            self._logger.info("Transfer done!")

        # Let the device know we're done
        if not self._endTransmission():
            return False

        return success
