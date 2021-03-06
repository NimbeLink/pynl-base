"""
Provides handling of UICR actions using a DAP's AHB-AP interface

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import time

from .ahb import Ahb

class Uicr:
    """A UICR interface via a Debug Access Port
    """

    class Registers:
        """The nRF9160 UICR register set

        There's also a wonky additional register in the NVMC peripheral that
        gives Non-Secure debugger access to APPROTECT when Secure debugger
        access is prohibited, so that's what the NsNvmcStart is meant for
        """

        Start                   = 0x00FF8000
        NsNvmcStart             = 0x40039000

        ApProtect               = Start + 0x000
        SecureApProtect         = Start + 0x02C
        EraseProtect            = Start + 0x030
        Otp                     = Start + 0x108
        WriteUicrNs             = NsNvmcStart + 0x588

    def __init__(self, ahb: Ahb) -> None:
        """Creates a new UICR-aware AHB-AP

        :param self:
            Self
        :param ahb:
            The AHB to use

        :return none:
        """

        self._ahb = ahb

    def enableApProtect(self, secure: bool) -> None:
        """Attempts to enable Access Port protection

        :param self:
            Self
        :param secure:
            Whether to do this for the Secure or Non-Secure context

        :return none:
        """

        # Our utilities might in turn try to use debugger stuff, so be lazy
        # about our import
        import nimbelink.utils as utils

        if secure:
            chunks = [
                utils.Flash.Chunk(
                    start = self.Registers.SecureApProtect,
                    data = [0x00, 0x00, 0x00, 0x00]
                )
            ]
        else:
            chunks = [
                utils.Flash.Chunk(
                    start = self.Registers.WriteUicrNs,
                    data = [0x71, 0x5A, 0xBE, 0xAF]
                )
            ]

        self._ahb.setSecureState(secure = secure)

        # nrfjprog seems to have some issues properly writing to UICR, at least
        # through their pynrfjprog API interface, so don't use passthrough, use
        # our DAP implementation
        utils.Flash.writeChunks(ahb = self._ahb, chunks = chunks, erase = False, passthrough = False)
