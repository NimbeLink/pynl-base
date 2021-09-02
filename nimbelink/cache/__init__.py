"""
NimbeLink package caching

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import os

import nimbelink

from .cache import Cache

__all__ = [
    "Cache",

    "getCache"
]

def getCache(namespace: str = "root") -> Cache:
    """Gets a NimbeLink cache

    :param namespace:
        The namespace to get a cache for

    :return None:
        Failed to get cache
    :return Cache:
        The cache
    """

    # Grab the cache stored in our base 'nimbelink' package's installation
    # directory
    return Cache(
        directory = os.path.join(
            os.path.dirname(nimbelink.__file__),
            "__pycache__",
            ".pynlcache"
        ),
        namespace = namespace
    )
