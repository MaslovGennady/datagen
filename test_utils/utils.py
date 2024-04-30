"""
Testing utils
"""

from uuid import UUID
from datetime import datetime


def is_valid_uuid(value):
    """
    Check of uuid correctness
    :param value: boolean
    :return:
    """
    try:
        uuid_obj = UUID(value, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == value


def strftime_format(format):
    """
    Check of value corresponds date format or not
    :param format: date format
    :return:
    """

    def func(value):
        try:
            datetime.strptime(value, format)
        except ValueError:
            return False
        return True

    func.__doc__ = f"should use date format {format}"
    return func
