"""
A configuration option

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import functools
import typing

@functools.total_ordering
class Option:
    """This class represents a configuration option

    Usually an option's value is not set on Option creation and is set from the
    Config class using the .value = <value> notation. The value of the object
    can be retrieved with the value property.

    Example:

        # Somewhere in initialization
        option = Option("my_option")
        config.add_option(option)

        # config sets option's value

        # Somewhere in initialization
        option = Option("my_option")
        config.add_option(option)

        # Somewhere in program main run
        print(option.value)
    """

    @staticmethod
    def toBool(value):
        """Converts a value to a boolean

        :param value:
            The value to convert

        :raise TypeError:
            Invalid boolean-like value

        :return True:
            True
        :return False:
            False
        """

        if isinstance(value, bool):
            return value

        if value.lower() in ["yes", "y", "true", "t", "1"]:
            return True

        if value.lower() in ["no", "n", "false", "f", "0"]:
            return False

        raise TypeError(f"Failed to convert '{value}' to a boolean")

    def __init__(
        self,
        name: str,
        type: object = None,
        value: object = None,
        choices: typing.List[object] = None
    ):
        """Creates a new configuration option

        :param self:
            Self
        :param name:
            The name of this option
        :param type:
            The type of value this contains
        :param value:
            The value of this option
        :param choices:
            The available values to choose from

        :return none:
        """

        self._name = name
        self._type = type
        self._value = value
        self._choices = choices

    def __lt__(self, other: "Option") -> bool:
        """Checks if we're less than another option

        The comparison is done by comparing our name to theirs, meaning any
        sorting of options will result in an alphabetized list.

        :param self:
            Self
        :param other:
            The thing to compare us to

        :return True:
            We are 'less' than them
        :return False:
            We are 'greater than or equal' to them
        """

        return self._name < other._name

    @property
    def name(self):
        """Get the name of an option

        :param self:
            Self

        :return String:
            The name of the option
        """

        return self._name

    @property
    def type(self):
        """Get the value type of an option

        :param self:
            Self

        :return object:
            The value type of the option
        """

        if self._value is not None:
            return type(self._value)

        return self._type

    @property
    def choices(self):
        """Gets the available values to choose from

        :param self:
            Self

        :return List[object]:
            The available choices
        """

        return self._choices

    @property
    def value(self):
        """Get the value of an option

        :param self:
            Self

        :return object:
            The value of the option or None
        """

        return self._value

    def _getValue(self, newValue):
        """Gets a proper value from an incoming value

        :param self:
            Self
        :param newValue:
            The value to use to get a proper value from

        :raise TypeError:
            Failed to get value

        :return object:
            The value
        """

        # If we don't know our type, we will just have to use it directly
        if self._type is None:
            return newValue

        # If it's the correct type, use it
        if isinstance(newValue, self._type):
            return newValue

        # If this is a string, try to parse it and use that result as our value
        if isinstance(newValue, str):
            try:
                return self._type(newValue)

            except ValueError:
                pass

        # This isn't our type, it isn't a parsable string, or the parsing
        # failed, so we can't use it
        raise TypeError(f"Invalid type {type(newValue)} for option '{self._name}' of type {self._type}")

    @value.setter
    def value(self, newValue):
        """Set the value of an option

        This is usually used with in the Config class

        :param self:
            Self
        :param newValue:
            The value to set the option to

        :return none:
        """

        # Get a proper value for this incoming thing
        newValue = self._getValue(newValue = newValue)

        # If we have a defined set of choices, make sure this is valid
        if self._choices is not None:
            if newValue not in self._choices:
                raise TypeError(f"Invalid value {newValue} for choices {self._choices}")

        # Great, got our new value
        self._value = newValue

    def __str__(self):
        """Get a string representation of the option

        :param self:
            Self

        :return String:
            Us as a string
        """

        string = f"{self._name}:"

        if self._value != None:
            string += f" {self._value}"

        return string
