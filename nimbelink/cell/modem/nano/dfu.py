"""
Provides DFU utilities for the Skywire Nano

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee.  No other use or
disclosure of this software is permitted. Portions of this software may be
subject to third party license terms as specified in this software, and such
portions are excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import struct

class Dfu:
    HeaderSize = 64
    """How large headers are"""

    Magic = 0xecce1347
    """Our 'magic' at the front of headers"""

    class Type:
        """A target image that can be updated via DFU
        """

        Stack       = 0
        Application = 1
        Modem       = 2
        Key         = 3
        Partition   = 4

    @staticmethod
    def needsReboot(type: "Dfu.Type") -> bool:
        """Gets if a DFU type needs a reboot

        :param type:
            The type to check

        :return True:
            DFU type needs a reboot
        :return False:
            DFU type does not need a reboot
        """

        # Keys and partitions do not need automated reboots
        if (type == Dfu.Type.Key) or (type == Dfu.Type.Partition):
            return False

        # Everything else will need a reboot
        return True

    @staticmethod
    def format(data: bytearray, type: "Dfu.Type") -> bytearray:
        """Adds a header to binary data meant for DFU

        :param data:
            The data to add a header to
        :param type:
            The type of data this is

        :return bytearray:
            The formatted data
        """

        # If the data already contains magic, it's probably already formatted
        if (len(data) > 3) and (struct.unpack("I", data[0:4])[0] == Dfu.Magic):
            return data

        # Add magic
        headerData = struct.pack("I", Dfu.Magic)

        # Add the type
        headerData += struct.pack("I", type)

        # Add the length
        headerData += struct.pack("I", len(data))

        # Get how much header space we have left to generate
        padWords = int((Dfu.HeaderSize - len(headerData)) / 4)

        # Pad the rest of the header
        for i in range(padWords):
            headerData += struct.pack("I", 0)

        # Prefix the data with the header contents
        return headerData + data
