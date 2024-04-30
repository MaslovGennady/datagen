import pandas as pd
import numpy as np
import datatest as dt

from .utils import strftime_format
from datagen.utils import logging_info
from datagen.const import ColumnType, FDUseMode


def validate_datetime_column(df, column):
    """
    Part of testing script consisting of validation of datetime column in according to generate method
    :param df: dataset
    :param column: column class
    :return:
    """
    RE_DATETIME = ""
    PY_DATETIME = ""
    if column.date_kind == ColumnType.DATE:
        RE_DATETIME = r"^[1-9][0-9]{3}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
        PY_DATETIME = "%Y-%m-%d"
    elif column.date_kind == ColumnType.DATETIME:
        RE_DATETIME = r"^[1-9][0-9]{3}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) ([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$"
        PY_DATETIME = "%Y-%m-%d %H:%M:%S"
    dt.validate.regex(df[column.name], RE_DATETIME)
    dt.validate(df[column.name], strftime_format(PY_DATETIME))
    # Date values compare scheme
    # DataFrame object to_datetime-> numpy.datetime64
    # class datetime.datetime datetime64-> numpy.datetime64
    # then compare
    if column.sequence_start_value:
        dt.validate.interval(
            pd.to_datetime(df[column.name], format=PY_DATETIME),
            min=np.datetime64(column.sequence_start_value),
        )
    elif column.datetime_set_max_datetime:
        dt.validate.interval(
            pd.to_datetime(df[column.name], format=PY_DATETIME),
            np.datetime64(column.datetime_set_min_datetime),
            np.datetime64(column.datetime_set_max_datetime),
        )
    elif column.constant:
        # it's a bad idea to set([timestamp,...])
        dt.validate(df[column.name], column.date_to_str(column.constant))
    elif column.constant_list:
        dt.validate.subset(
            df[column.name],
            set([column.date_to_str(value) for value in column.constant_list]),
        )
    elif column.global_constant_list:
        # no need to date_to_str here, global objects are strings
        dt.validate.subset(df[column.name], set(column.global_constant_list.data))
    elif column.functional_dependency:
        if column.functional_dependency_use_mode == FDUseMode.GENERATE_FROM_KEYS:
            dt.validate.subset(df[column.name], set([key[0] for key in column.functional_dependency.keys]))
        elif column.functional_dependency_use_mode == FDUseMode.CHOOSE_FROM_VALUES:
            dt.validate.subset(
                df[column.name],
                set(
                    [
                        value[column.functional_dependency_value_position]
                        for value in column.functional_dependency.data.values()
                    ]
                ),
            )
    else:
        logging_info(f"No method-based validation applied to column {column.name}")
