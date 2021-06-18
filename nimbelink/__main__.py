"""
The main entry point for the NimbeLink package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import logging
import sys

import nimbelink.command as command

def main():
    """Handles commands

    :param none:

    :return none:
    """

    # Get a logger for everything
    root = logging.getLogger()

    # Everything gets 'info'-level logging
    root.setLevel(logging.INFO)

    # Make a handler for logging to standard output
    handler = logging.StreamHandler()

    # Add the handler to our root loggers
    root.addHandler(handler)

    result = command.run()
    sys.exit(result)

if __name__ == "__main__":
    main()
