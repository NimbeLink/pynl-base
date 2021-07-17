"""
Skywire modem SIM utilities

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

class Sim:
    """Skywire modem SIM utilities

    This module will offer access to a platform's SIMs. An instance of a SIM is
    also referred to as a 'SIM'.

    SIMs can be accessed either by a familiar name or by their 'ID'. The list of
    available SIM names and the meaning of a SIM's ID are up to the platform
    implementing the Sim sub-module class.

    A given physical SIM can be 'fixed' or not -- that is, it's expected to
    always have the same ICCID or not. An example would be a soldered SIM whose
    ICCID cannot be changed. A counterexample would be a SIM cage, whose
    physical SIM can be removed and replaced with another SIM.

    This sub-module will offer access to all available SIMs by either their
    familiar name or their ID:

        modem.sim[0] ...
        modem.sim["mysim"] ...

    The currently-active SIM can also be accessed by a dedicated member:

        modem.sim.current ...

    The currently-active SIM can be selected by the same member:

        modem.sim.current = 0
        modem.sim.current = "mysim"

    A SIM's ICCID can be queried through a property in the SIM instance:

        modem.sim[0].iccid ...
        modem.sim.current.iccid ...

    If a SIM doesn't yet know its ICCID and it wasn't known at the time of
    instantiation, it will attempt to query the ICCID. On most platforms, only
    the currently-active SIM can be queried, meaning any uncached ICCID access
    will result in an exception.
    """

    class Instance:
        """A physical SIM
        """

        def __init__(
            self,
            id: int,
            name: str = None,
            fixed: bool = None,
            iccid: str = None
        ) -> None:
            """Creates a new physical SIM instance

            :param self:
                Self
            :param id:
                The ID of this SIM
            :param name:
                A familiar name for this SIM
            :param fixed:
                Whether or not this SIM can change or is 'fixed'
            :param iccid:
                This SIM's ICCID

            :return none:
            """

            if fixed is None:
                fixed = False

            self.id = id
            self.name = name
            self.fixed = fixed

            self._iccid = iccid

            self._sim = None

        def __str__(self) -> str:
            """Gets a string representation of us

            :param self:
                Self

            :return str:
                Us
            """

            string = f"{self.id} "

            if self.name is not None:
                string += f"({self.name}) "

            string += f": {self.iccid}"

            return string

        def _invalidate(self) -> None:
            """Invalidates this SIM's ICCID

            :param self:
                Self

            :return none:
            """

            # Only invalidate our ICCID if we aren't fixed
            if not self.fixed:
                self._iccid = None

        @property
        def iccid(self) -> str:
            """Gets this SIM's ICCID

            :param self:
                Self

            :return str:
                Our ICCID
            """

            # If we haven't cached our ICCID yet, try to do so
            if self._iccid is None:
                self._iccid = self._sim._getIccid(sim = self)

            return self._iccid

    def __init__(self, sims: typing.List["Sim.Instance"], current: int = None) -> None:
        """Creates a new SIM sub-module

        :param self:
            Self
        :param sims:
            Our available SIM instances

        :return none:
        """

        if current is None:
            current = 0

        for sim in sims:
            sim._sim = self

        self._sims = sims
        self._current = sims[current]

    def __len__(self) -> int:
        """Gets the number of SIMs available

        :param self:
            Self

        :return int:
            The number of SIMs available
        """

        return len(self._sims)

    def __getitem__(self, key: typing.Tuple[int, str]) -> "Sim.Instance":
        """Gets a SIM by name or ID

        :param self:
            Self
        :param key:
            Which item to get

        :raise TypeError:
            Invalid key type
        :raise KeyError:
            Failed to find SIM

        :return Sim.Instance:
            The SIM
        """

        if isinstance(key, str):
            sims = [sim for sim in self._sims if sim.name == key]

        elif isinstance(key, int):
            sims = [sim for sim in self._sims if sim.id == key]

        else:
            raise TypeError(f"Invalid type {type(key)} for SIM")

        if len(sims) < 1:
            raise KeyError(f"Failed to find {key} in SIMs")

        if len(sims) > 1:
            raise KeyError(f"{key} is ambiguous in SIMs")

        return sims[0]

    @property
    def current(self) -> "Sim.Instance":
        """Gets our current SIM

        :param self:
            Self

        :return Sim.Instance:
            Our current SIM
        """

        return self._current

    @current.setter
    def current(self, key: typing.Tuple[int, str]) -> None:
        """Sets our active SIM

        :param self:
            Self
        :param key:
            Which SIM to set

        :return none:
        """

        # Get the SIM
        sim = self[key]

        # Select the new SIM
        self._setActive(sim = sim)

        # We successfully changed SIMs, so notify our previous one it might be
        # invalidated
        self._current._invalidate()

        # We successfully selected the SIM, so note it's our current one
        self._current = sim

    def _setActive(self, sim: "Sim.Instance") -> None:
        """Sets the currently-selected SIM

        :param self:
            Self
        :param index:
            Which SIM to select

        :return none:
        """

        raise NotImplementedError(f"setActive() not implemented by {self.__class__.__name__}")

    def _getIccid(self, sim: "Sim.Instance") -> str:
        """Gets a SIM's ICCID

        :param self:
            Self
        :param index:
            The SIM whose ICCID to get

        :return str:
            The current SIM's ICCID
        """

        raise NotImplementedError(f"@iccid not implemented by {self.__class__.__name__}")
