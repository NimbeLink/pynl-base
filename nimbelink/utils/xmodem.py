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
import time
import serial

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
        def getInversePacketId(cls, packetId):
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
        def getPacket(cls, packetData, packetId):
            """Gets an XMODEM packet from data and an ID

            :param cls:
                Class
            :param packetData:
                The data to packetize
            :param packetId:
                The ID of this packet

            :return Array of bytes:
                The packet
            """

            padLength = 0

            if len(packetData) <= 128:
                packetStart = cls.SmallStart
                padLength = 128 - len(packetData)
            else:
                packetStart = cls.LargeStart
                padLength = 1024 - len(packetData)

            # If we need to pad the packet, do so
            # Original protocol uses 0x1a as the padding character but 0xff
            # was done for west
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
        def getFirstPacketId(cls):
            """Gets the first packet ID in the sequence

            :param cls:
                Class

            :return 0x01:
                Always
            """

            return 0x01

        @classmethod
        def getNextPacketId(cls, packetId):
            """Gets the next packet ID in the sequence

            :param cls:
                Class
            :param packetId:
                The current packet ID

            :return Byte:
                The next packet ID
            """

            return (packetId + 1) & 0xFF

    def __init__(self, device: serial.Serial):
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
        self.packetId = Xmodem.Packet.getFirstPacketId()

    def _clear(self):
        """Clears our device's input/output buffers

        :param self:
            Self

        :return none:
        """

        while len(self._device.read_all()) > 0:
            self._device.reset_output_buffer()
            self._device.reset_input_buffer()

    def _startTransmission(self):
        """Starts XMODEM transmission

        :param self:
            Self

        :return True:
            Transmission started
        :return False:
            Failed to start transmission
        """

        # Initialize our packet ID
        self.packetId = Xmodem.Packet.getFirstPacketId()

        # Clear out any previous data in the serial buffers
        self._clear()

        # Try for 30 seconds to get the starting NAK, discarding single
        # bytes until we timeout or get a NAK
        beginTime = time.time()
        while (time.time() - beginTime) < 30:
            # Try reading a single byte from the serial device
            start = self._device.read(1)
            # Make sure we didn't timeout
            if start:
                # If we got a NAK return success
                if start[0] == Xmodem.Packet.Nak:
                    return True
                # Log the non-NAK byte
                else:
                    self._logger.debug(start)

        # Failed to get starting NAK
        self._logger.error("Failed to get starting NAK")
        return False

    def _sendData(self, packetData):
        """Sends a packet to a device

        :param self:
            Self
        :param data:
            The data to send

        :return True:
            Packet sent and acknowledged
        :return False:
            Failed to send packet
        """

        response = bytes([Xmodem.Packet.Nak])
        beginTime = time.time()

        # Try for 40 seconds to send the packet
        while time.time() - beginTime < 40:
            # Get the packet
            packet = Xmodem.Packet.getPacket(
                packetData = packetData,
                packetId = self.packetId
            )

            self._logger.debug("Sending %s", ascii(packet))

            # If we aren't using flow control, chunk the data
            if not self._device.rtscts:
                writeLength = 0

                packetBytes = list(packet)

                while True:
                    if len(packetBytes) < 1:
                        break

                    time.sleep(0.1)

                    writeLength += \
                            self._device.write(packetBytes[0:Xmodem.ChunkSize])

                    packetBytes = packetBytes[Xmodem.ChunkSize:]

            # Else, just spit everything out
            else:
                writeLength = self._device.write(packet)

            # If that failed, that's a paddlin'
            if writeLength != len(packet):
                self._logger.error("Failed to send all bytes (%d/%d)",
                                                    writeLength, len(packet))
                return False

            # Wait for a response
            response = self._device.read(1)

            # If that failed, that's a paddlin'
            if (response is None) or (len(response) < 1):
                self._logger.error("Failed to get response")
                return False

            self._logger.debug("Received %s", ascii(response.decode()))

            if response[0] == Xmodem.Packet.Ack:
                # Modem ACKed packet
                break
            else:
                # Try again in two seconds if the modem didn't ACK
                self._logger.warning("Failed to get ACK, reattempting...")
                time.sleep(2) 

        # If it wasn't acknowledged, that's a paddlin'
        if response[0] != Xmodem.Packet.Ack:
            self._logger.error("Failed to get ACK (%s)", ascii(response[0]))
            return False

        # Use the next packet ID next time
        self.packetId = Xmodem.Packet.getNextPacketId(packetId = self.packetId)

        return True

    def _endTransmission(self):
        """Ends XMODEM transmission

        :param self:
            Self

        :return True:
            Transmission ended successfully
        :return False:
            Ending transmission failed
        """

        # Stop transmission
        self._device.write(bytearray([Xmodem.Packet.EndOfTransmission]))

        # Try for 30 seconds to get the last NAK, discarding single bytes until
        # we timeout or get a NAK
        beginTime = time.time()
        while (time.time() - beginTime) < 30:
            # Try reading a single byte from the serial device
            start = self._device.read(1)
            # Make sure we didn't timeout
            if start:
                # If we got an ACK return success
                if start[0] == Xmodem.Packet.Ack:
                    return True
                # Log the non-ACK byte
                else:
                    self._logger.debug(start)

        return False

    def transfer(self, data, packetSize = None):
        """Transfers data using XMODEM

        :param self:
            Self
        :param data:
            Bytes-like data to send
        :param packetSize:
            The size of the packets to use

        :raise ValueError:
            Invalid packet size

        :return True
            File sent
        :return False
            Failed to send file
        """
        # Use a packet size of 1024 (XMODEM-1K) by default
        if packetSize is None:
            packetSize = 1024
        # Verify that the packet size is valid
        if packetSize not in Xmodem.Packet.TransferSizes:
            raise ValueError("Can't use packet size of {}!".format(packetSize))

        # Result of transfer is failure until proven otherwise
        success = False
        # Number of bytes from data that we have sent to the modem
        count = 0

        # If we fail to kick off transmission, that's a paddlin'
        if not self._startTransmission():
            return False

        # Try sending the data to the modem
        while True:
            # Delay a little bit to help with stability
            time.sleep(0.01)

            # Try to read the next chunk of data
            packetData = data[count : count + packetSize]

            # If we're out of data, move on
            if len(packetData) < 1:
                success = True
                break

            # If we fail to send the data, stop
            if not self._sendData(packetData = packetData):
                break
            # Use the next chunk of data
            count += len(packetData)

        # Let the device know we're done
        if not self._endTransmission():
            return False

        return success
