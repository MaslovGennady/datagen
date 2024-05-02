"""
Common generation utils
"""

import logging
import sys
import random as rnd
from .const import ChooseMethod, FDUseMode


def logging_error(*args: object):
    """
    Logging of error and program exit
    :param args: list of messages to log
    :return:
    """
    text = "\n".join(map(str, args))
    logging.error(text)
    sys.exit(0)


def logging_info(*args: object):
    """
    Logging of info messages
    :param args: list of messages to log
    :return:
    """
    text = "\n".join(map(str, args))
    logging.info(text)


def logging_warning(*args: object):
    """
    Logging of warning messages
    :param args: list of messages to log
    :return:
    """
    text = "\n".join(map(str, args))
    logging.warning(text)


def generate_constant_list_value(column):
    """
    Common method for all columns to generate constant list value
    :param column: column class object
    :return:
    """
    idx = None
    if column.constant_list_choose_method == ChooseMethod.RANDOM:
        idx = rnd.randint(0, column.constant_list_values_length - 1)

    if column.constant_list_choose_method == ChooseMethod.ROUND_ROBIN:
        idx = column.constant_list_current_idx
        column.constant_list_current_idx = (
            column.constant_list_current_idx + 1
        ) % column.constant_list_values_length
    return column.constant_list[idx]


def generate_global_constant_list_value(column):
    """
    Common method for all columns to generate global constant list value
    :param column: column class object
    :return:
    """
    idx = None
    if column.global_constant_list_choose_method == ChooseMethod.RANDOM:
        idx = rnd.randint(0, column.global_constant_list.data_length - 1)

    if column.global_constant_list_choose_method == ChooseMethod.ROUND_ROBIN:
        idx = column.global_constant_list_current_idx
        column.global_constant_list_current_idx = (
            column.global_constant_list_current_idx + 1
        ) % column.global_constant_list.data_length
    return column.global_constant_list.get_value_by_id(idx)


def generate_functional_dependency_value(column):
    """
    Common method for all columns to generate FD value
    :param column: column class object
    :return:
    """
    idx = None
    if column.functional_dependency_use_mode == FDUseMode.GENERATE_FROM_KEYS:
        if column.functional_dependency_choose_method == ChooseMethod.ROUND_ROBIN:
            idx = column.functional_dependency_current_idx
            column.functional_dependency_current_idx = (
                column.functional_dependency_current_idx + 1
            ) % column.functional_dependency.keys_cnt

        if column.functional_dependency_choose_method == ChooseMethod.RANDOM:
            idx = rnd.randint(0, column.functional_dependency.keys_cnt - 1)

        return column.functional_dependency.get_key_by_idx(idx)

    if column.functional_dependency_use_mode == FDUseMode.CHOOSE_FROM_VALUES:
        key = [
            str(column.dataset.row[column_name])
            for column_name in column.dataset_columns_as_fd_key
        ]
        key = tuple(key)
        return column.functional_dependency.get_value_by_key(
            key, column.functional_dependency_value_position
        )
