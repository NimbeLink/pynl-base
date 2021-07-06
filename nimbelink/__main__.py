"""
The main entry point for the NimbeLink package

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import sys

import nimbelink.command as command

def main():
    """Handles commands

    :param none:

    :return none:
    """

    # Run commands, assuming they're coming from sys.argv
    result = command.run()

    # Exit with the result of the command running
    sys.exit(result)

if __name__ == "__main__":
    main()
