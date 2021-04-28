###
 # \file
 #
 # \brief Sends data using an XMODEM interface
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

            # If we should pad the packet, do so
            if padLength > 0:
                for i in range(padLength):
                    packetData += bytearray([0xFF])

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

    def __init__(self, device):
        """Creates a new XMODEM interface

        :param self:
            Self
        :param device:
            Our UART device

        :return none:
        """

        self._logger = logging.getLogger(__name__)

        self._device = device

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

        # Try for a bit to get our initial NAK byte
        for i in range(5):
            start = self._device.read()

            if len(start) > 0:
                self._logger.debug("Received {}".format(ascii(start.decode())))

                # If we got the initial NAK, great, move on
                if start[0] == Xmodem.Packet.Nak:
                    return True

                # We must have gotten some other garbage, so try clearing the
                # serial port and go back around the horn for another try
                self._clear()

            if i < 4:
                time.sleep(1)

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

        # Get the packet
        packet = Xmodem.Packet.getPacket(
            packetData = packetData,
            packetId = self.packetId
        )

        self._logger.debug("Sending {}".format(ascii(packet)))

        # If we aren't using flow control, chunk the data
        if not self._device.rtscts:
            writeLength = 0

            bytes = list(packet)

            while True:
                if len(bytes) < 1:
                    break

                time.sleep(0.1)

                writeLength += self._device.write(bytes[0:Xmodem.ChunkSize])

                bytes = bytes[Xmodem.ChunkSize:]

        # Else, just spit everything out
        else:
            writeLength = self._device.write(packet)

        # If that failed, that's a paddlin'
        if writeLength != len(packet):
            self._logger.error("Failed to send all bytes ({}/{})".format(writeLength, len(packet)))
            return False

        # Wait for a response
        response = self._device.read(1)

        # If that failed, that's a paddlin'
        if (response == None) or (len(response) < 1):
            self._logger.error("Failed to get response")
            return False

        self._logger.debug("Received {}".format(ascii(response.decode())))

        # If it wasn't acknowledged, that's a paddlin'
        if response[0] != Xmodem.Packet.Ack:
            self._logger.error("Failed to get ACK ({})".format(response[0]))
            return False

        # Use the next packet ID next time
        self.packetId = Xmodem.Packet.getNextPacketId(packetId = self.packetId)

        return True

    def _endTransmission(self):
        """Ends XMODEM transmission

        :param self:
            Self

        :return True:
            Always
        """

        # Stop transmission
        self._device.write([Xmodem.Packet.EndOfTransmission])

        return True

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

        if packetSize == None:
            packetSize = 1024

        if packetSize not in Xmodem.Packet.TransferSizes:
            raise ValueError("Can't use packet size of {}!".format(packetSize))

        # Guilty until proven innocent
        success = False

        count = 0

        # Make sure nothing is left over
        self._clear()

        # If we fail to kick off transmission, that's a paddlin'
        if not self._startTransmission():
            return False

        self._clear()

        while True:
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

            count += len(packetData)

        # Let the device know we're done
        self._endTransmission()

        return success
