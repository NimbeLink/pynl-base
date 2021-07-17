"""
Skywire modem application utilities

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

class App:
    """Skywire modem application utilities

    This module will offer access to a platform's apps. An instance of an app is
    also referred to as an 'app'.

    Apps can be accessed either by a familiar name or by their 'ID'. The list of
    available app names and the meaning of an app's ID are up to the platform
    implementing the App sub-module class.

    This sub-module will offer access to all available apps by either their
    familiar name or their ID:

        modem.app[0] ...
        modem.app["myapp"] ...

    An app's version can be queried through a property in the app instance:

        modem.app[0].version ...

    If an app doesn't yet know its version and it wasn't known at the time of
    instantiation, it will attempt to query the version.
    """

    class Instance:
        """A particular application instance
        """

        def __init__(
            self,
            id: int,
            name: str,
            version: str = None
        ) -> None:
            """Creates a new application instance

            :param self:
                Self
            :param id:
                The ID of this application
            :param name:
                The familiar name of this application
            :param verison:
                This app's version

            :return none:
            """

            self.id = id
            self.name = name

            self._version = version

            self._app = None

        def __str__(self) -> str:
            """Gets a string representation of us

            :param self:
                Self

            :return str:
                Us
            """

            return f"{self.id} ({self.name}) : {self.version}"

        @property
        def version(self) -> str:
            """Gets this application's version

            :param self:
                Self

            :return str;
                This application's version
            """

            # If we were told what our version is, use that
            if self._version is not None:
                return self._version

            # If we're getting our live version, always re-query it
            return self._app._getVersion(app = self)

    def __init__(self, apps: typing.List["App.Instance"]) -> None:
        """Creates a new app sub-module

        :param self:
            Self
        :param apps:
            Our available apps

        :return none:
        """

        for app in apps:
            app._app = self

        self._apps = apps

    def __len__(self) -> int:
        """Gets the number of apps available

        :param self:
            Self

        :return int:
            The number of apps available
        """

        return len(self._apps)

    def __getitem__(self, key: typing.Tuple[int, str]) -> "App.Instance":
        """Gets an application by name or ID

        :param self:
            Self
        :param key:
            Which item to get

        :raise TypeError:
            Invalid key type
        :raise KeyError:
            Failed to find app

        :return App.Instance:
            The app
        """

        if isinstance(key, str):
            apps = [app for app in self._apps if app.name == key]

        elif isinstance(key, int):
            apps = [app for app in self._apps if app.id == key]

        else:
            raise TypeError(f"Invalid type {type(key)} for app")

        if len(apps) < 1:
            raise KeyError(f"Failed to find {key} in apps")

        if len(apps) > 1:
            raise KeyError(f"{key} is ambiguous in apps")

        return apps[0]

    def _getVersion(self, app: "App.Instance") -> str:
        """Gets an application's version

        :param self:
            Self
        :param app:
            The appliaction whose version to get

        :return str:
            The application's version
        """

        raise NotImplementedError(f"@versions not implemented by {self.__class__.__name__}")
