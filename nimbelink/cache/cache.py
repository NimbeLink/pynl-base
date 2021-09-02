"""
A simple file-based cache

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import diskcache

class Cache:
    """A simple file-based cache
    """

    def __init__(self, namespace: str, directory: str) -> None:
        """Creates a new cache

        :param self:
            Self
        :param namespace:
            The namespace this cache resides in
        :param directory:
            The directory containing the cache itself

        :return none:
        """

        self._namespace = namespace
        self._directory = directory

        # Don't bother getting our backend until it's actually requested
        self._backend = None

    def _makeKey(self, key: str) -> str:
        """Gets a namespaced key

        :param self:
            Self
        :param key:
            The key to add a namespace to

        :return str:
            The namespaced key
        """

        # If someone did us dirty, just return the key
        if self._namespace is None:
            return key

        return f"{self._namespace}.{key}"

    @property
    def backend(self) -> diskcache.Cache:
        """Gets our diskcache backend

        :param self:
            Self

        :return None:
            Failed to get our cache
        :return diskcache.Cache:
            Our cache
        """

        # If we haven't gotten our cache yet, try to get it
        if self._backend is None:
            try:
                # Get our base NimbeLink package's location as our cache
                # location
                self._backend = diskcache.Cache(self._directory)

            except Exception:
                pass

        return self._backend

    def get(self, key: str) -> object:
        """Gets a value from the cache

        :param self:
            Self
        :param key:
            The key to get a value from

        :return None:
            No cached value found
        :return object:
            The cached value
        """

        if self.backend is None:
            return None

        return self.backend.get(key = self._makeKey(key = key))

    def set(self, key: str, value: object) -> bool:
        """Sets a value in the cache

        :param self:
            Self
        :param key:
            The key to set a value for
        :param value:
            The value to set

        :return True:
            Value cached
        :return False:
            Failed to cache value
        """

        if self.backend is None:
            return False

        return self.backend.set(key = self._makeKey(key = key), value = value)
