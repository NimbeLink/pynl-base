###
 # \file
 #
 # \brief Skywire modem application utilities
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

class App:
    """Skywire modem application utilities
    """

    class Version:
        """A version of a firmware image on a Skywire
        """

        def __init__(self, name, value):
            """Creates a new firmware image version

            :param self:
                Self
            :param name:
                The name of this firmware image
            :param value:
                The value of this firmware image's version

            :return none:
            """

            self.name = name
            self.value = value

        def __str__(self):
            """Creates a string representation of a version

            :param self:
                Self

            :return String:
                Us
            """

            return "{}: {}".format(self.name, self.value)

        def __eq__(self, other):
            """Compares to another version

            :param self:
                Self
            :param other:
                The version to compare to

            :return True:
                We are equal
            :return False:
                We are not equal
            """

            if other == None:
                return False

            if (other.name != self.name) or (other.value != self.value):
                return False

            return True

        def __ne__(self, other):
            """Compares to another version

            :param self:
                Self
            :param other:
                The version to compare to

            :return True:
                We are not equal
            :return False:
                We are equal
            """

            return not (self == other)
