# NimbeLink Python Package

## Installation

This repository is a full Python package that can be installed using the 'git+'
URL form, either directly or as a dependency for another project. It can also be
checked out using Git and installed locally using:

    python -m pip install [options] -e <dir>

The installation will result in an 'entry point' (in Python nomenclature) called
'nimbelink' that provides a root command for any sub-commands provided by this
repository and any additional repositories that register with the module and
command subsystems.

If your path includes your Python installation's console scripts directory, you
can run the root 'nimbelink' command directly:

    nimbelink ...

Otherwise, it can be run as a package 'module':

    python -m nimbelink ...

## Package Design

In general, this package is intended to be wholly available from a simple:

    import nimbelink

without having to dive further into sub-packages and import them manually. That
is, you can do the following:

    import nimbelink

    nimbelink.utils.Xmodem(...)

Any sub-packages are still available for direct, initial import:

    import nimbelink.command
    import nimbelink.utils as utils

    nimbelink.command.Command(...)
    utils.Xmodem(...)
