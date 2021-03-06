"""
Provides base Debug Access Port functionality

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import logging
import time

from pynrfjprog import API
from pynrfjprog import APIError

class Dap:
    """A Debug Access Port
    """

    def __init__(self, *args, serialNumber: str = None, **kwargs) -> None:
        """Creates a new DAP

        :param self:
            Self
        :param *args:
            Positional arguments
        :param serialNumber:
            The serial number of the debugger to select; None if any/the only
            debugger
        :param **kwargs:
            Keyword arguments

        :return none:
        """

        self.api = API.API(*args, **kwargs, device_family = "NRF91")

        self.api.open()

        if serialNumber is None:
            self.api.connect_to_emu_without_snr()
        else:
            self.api.connect_to_emu_with_snr(serial_number = serialNumber)

        dllVersion = self.api.dll_version()

        logging.getLogger(__name__).info(f"Debugger using DLL version {dllVersion[0]}.{dllVersion[1]}{dllVersion[2]}")

    def __del__(self) -> None:
        """Deletes a DAP

        :param self:
            Self

        :return none:
        """

        if hasattr(self, "api"):
            self.api.close()

    def read(self, port: int, register: int) -> int:
        """Reads from an address in an access port

        :param self:
            Self
        :param port:
            The access port to read from
        :param register:
            The register to read

        :return Integer:
            The value in the register
        """

        return self.api.read_access_port_register(port, register)

    def write(self, port: int, register: int, value: int) -> None:
        """Writes a value to an access port

        :param self:
            Self
        :param port:
            The access port to write to
        :param register:
            The register to write
        :param value:
            The value to write to the register

        :return none:
        """

        self.api.write_access_port_register(port, register, value)
