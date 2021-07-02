"""
Skywire Nano SIM resources

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import nimbelink.cell.modem as modem
import nimbelink.cell.modem.skywire as skywire

class Sim(skywire.Sim):
    """Skywire Nano SIM resources
    """

    def __init__(self, nano: "SkywireNano") -> None:
        """Creates a new GPIO sub-module

        :param self:
            Self
        :param nano:
            The Skywire Nano we're attached to

        :return none:
        """

        super().__init__(sims = [
            skywire.Sim.Instance(id = 0, name = "soldered", fixed = True),
            skywire.Sim.Instance(id = 1, name = "caged", fixed = False)
        ])

        self._nano = nano

    def _setActive(self, sim: skywire.Sim.Instance) -> None:
        """Sets our active SIM

        :param self:
            Self
        :param sim:
            Which SIM to select

        :raise AtError:
            Failed to select SIM

        :return none:
        """

        response = self._nano.at.sendCommand(f"AT#SIMSELECT={sim.id}")

        if not response:
            raise modem.AtError(response)

    def _getIccid(self, sim: skywire.Sim.Instance) -> str:
        """Gets our current SIM's ICCID

        :param self:
            Self

        :raise AtError:
            Failed to get ICCID

        :return str:
            The ICCID
        """

        # If this isn't our active SIM, this won't work
        if sim != self._current:
            raise ValueError(f"Cannot query SIM ICCID when not active ({sim} != {self._current}")

        response = self._nano.at.sendCommand("AT#ICCID?")

        if not response:
            raise modem.AtError(response)

        lines = response.lines

        if len(lines) < 1:
            raise modem.AtError(response, "ICCID not in response")

        return lines[0]
