"""
AT interface utilities

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from nimbelink.cell.at.cmeError import CmeError
from nimbelink.cell.at.cmsError import CmsError

class Result(object):
    """A result of an AT command
    """

    class Error:
        """An error result
        """

        General = 0
        Cme     = 1
        Cms     = 2
        """The error variants"""

        def __init__(self, variant, code = None):
            """Creates a new error

            :param self:
                Self
            :param variant:
                Which error variant we are
            :param code:
                An error code, if any

            :raise ValueError:
                Invalid variant and code combination

            :return none:
            """

            # Make sure they're doing sensible things
            if (code == None) and (variant != Result.Error.General):
                raise ValueError("Need a code for non-general errors!")

            self.variant = variant
            self.code = code

        def __eq__(self, other):
            """Compares us to another error

            :param self:
                Self
            :param other:
                The error to compare to

            :return True:
                We are equal
            :return False:
                We differ
            """

            if other == None:
                return False

            if (self.variant != other.variant) or (self.code != other.code):
                return False

            return True

        def __ne__(self, other):
            """Compares us to another error

            :param self:
                Self
            :param other:
                The error to compare to

            :return True:
                We differ
            :return False:
                We are equal
            """

            return not (self == other)

        def __str__(self):
            """Gets a string representation of the error

            :param self:
                Self

            :return String:
                Us
            """

            if self.variant == Result.Error.General:
                return "ERROR"

            if self.variant == Result.Error.Cme:
                return "CME ERROR: {}".format(CmeError.getName(self.code))

            if self.variant == Result.Error.Cms:
                return "CMS ERROR: {}".format(CmsError.getName(self.code))

            return "UNKNOWN ERROR"

        @staticmethod
        def makeFromString(string):
            """Gets the error from a string

            :param string:
                The string to decode

            :return None:
                Failed to look up error
            :return Error:
                The error
            """

            # Assume this is a generic error with no error code
            variant = Result.Error.General
            code = None

            # Sometimes the strings start with '+', so remove that if present
            if string.startswith("+"):
                string = string[1:]

            # If this is the basic error, nothing left to do
            if string == "ERROR":
                return Result.Error(
                    variant = Result.Error.General,
                    code = None
                )

            # If the last line starts with 'CME', it's a CME error
            if string.startswith("CME"):
                variant = Result.Error.Cme

            # Else, if the last line starts with 'CMS', it's a CMS error
            elif string.startswith("CMS"):
                variant = Result.Error.Cms

            # Else, we don't know how to parse this
            else:
                return None

            # Get the variant and code/name fields
            fields = string.split(":")

            # If that failed, that's a paddlin'
            if len(fields) < 2:
                return None

            # Strip off any whitespace
            name = fields[1].lstrip()

            # If we can parse this like an integer, then it's a code
            try:
                return Result.Error(
                    variant = variant,
                    code = int(name)
                )

            # Else, this must be an error name
            except ValueError:
                pass

            if variant == Result.Error.Cme:
                code = CmeError.getCode(name = name)
            else:
                code = CmsError.getCode(name = name)

            # If we failed to look up the code, that's a paddlin'
            if code == None:
                return None

            return Result.Error(
                variant = variant,
                code = code
            )

    @staticmethod
    def Ok():
        """Creates an 'OK' result

        :param none:

        :return Result:
            The 'OK' result
        """

        return Result(error = None)

    @staticmethod
    def CmeError(code):
        """Creates a CME error result

        :param code:
            The CME error code

        :return Result:
            The CME error result
        """

        return Result(error = Result.Error(variant = Result.Error.Cme, code = code))

    @staticmethod
    def CmsError(code):
        """Creates a CMS error result

        :param code:
            The CMS error code

        :return Result:
            The CMS error result
        """

        return Result(error = Result.Error(variant = Result.Error.Cms, code = code))

    def __init__(self, error):
        """Creates a new result

        :param self:
            Self
        :param error:
            The error, if any

        :return none:
        """

        self.error = error

    def __eq__(self, other):
        """Compares us to another result

        :param self:
            Self
        :param other:
            The result to compare to

        :return True:
            We are equal
        :return False:
            We differ
        """

        if other == None:
            return False

        if self.error != other.error:
            return False

        return True

    def __ne__(self, other):
        """Compares us to another result

        :param self:
            Self
        :param other:
            The result to compare to

        :return True:
            We differ
        :return False:
            We are equal
        """

        return not (self == other)

    def __bool__(self):
        """Gets a boolean representation of the result

        :param self:
            Self

        :return True:
            Result was a success
        :return False:
            Result was a failure
        """

        if self.error == None:
            return True

        return False

    def __str__(self):
        """Gets a string representation of the result

        :param self:
            Self

        :return String:
            Us
        """

        if self.error == None:
            return "OK"

        return "{}".format(self.error)

    @staticmethod
    def makeFromString(string):
        """Makes a result from the result output

        This assumes there is only a single line, it's the last one, and
        all line endings and/or whitespace have been stripped.

        :param string:
            The string to parse

        :return None:
            Failed to parse string
        :return Result:
            The result
        """

        if string == "OK":
            return Result.Ok()

        error = Result.Error.makeFromString(string = string)

        if error == None:
            return None

        return Result(error = error)
