"""
A debugger tool

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from .ahb import Ahb
from .ctrlAp import CtrlAp
from .dap import Dap
from .mailbox import Mailbox
from .uicr import Uicr

class Tool:
    """A debugger tool
    """

    def __init__(self, *args, **kwargs) -> None:
        """Creates a new debugger

        :param self:
            Self
        :param *args:
            Positional arguments for our DAP
        :param **kwargs:
            Keyword arguments for our DAP

        :return none:
        """

        self.dap = Dap(*args, **kwargs)

        self.ahb = Ahb(dap = self.dap)
        self.ctrlAp = CtrlAp(dap = self.dap)
        self.mailbox = Mailbox(ctrlAp = self.ctrlAp)
        self.uicr = Uicr(ahb = self.ahb)
