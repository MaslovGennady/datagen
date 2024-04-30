"""
Module for all constants
"""

from enum import Enum


DATAGEN_VALIDATE_ERROR = "Datagen validation error: "
DATAGEN_RUNTIME_ERROR = "Datagen runtime error: "


class WriteMethod(Enum):
    """
    Way of writing flat data
    """

    OVERWRITE = "overwrite"
    APPEND = "append"
    NEW = "new"


class ColumnType(Enum):
    """
    All column types
    """

    DATETIME = "datetime"
    DATE = "date"
    NUMBER = "number"
    STRING = "string"


class DatetimeGranularity(Enum):
    """
    Datetime granularity variants
    """

    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


class FDUseMode(Enum):
    """
    Mode of using functional dependency:
    Choose value from keys of FD
    Or get FD value by key
    """

    GENERATE_FROM_KEYS = "generate_from_keys"
    CHOOSE_FROM_VALUES = "choose_from_values"


class ChooseMethod(Enum):
    """
    Modes of choosing value from set of values
    """

    RANDOM = "random"
    ROUND_ROBIN = "round_robin"


class StructNames(Enum):
    """
    Common object type
    """

    FUNCTIONAL_DEPENDENCY = "functional_dependency"
    CONSTANT_LIST = "constant_list"
