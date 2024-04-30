import datatest as dt

from datagen.const import FDUseMode
from datagen.utils import logging_info


def validate_number_column(df, column):
    """
    Part of testing script consisting of validation of number column in according to generate method
    :param df: dataset
    :param column: column class
    :return:
    """
    dt.validate(df[column.name], int)

    if column.sequence_start_value is not None:
        dt.validate.interval(df[column.name], min=column.sequence_start_value)

    elif column.number_set_min_number is not None:
        dt.validate.interval(
            df[column.name],
            column.number_set_min_number * column.number_set_granularity,
            column.number_set_max_number * column.number_set_granularity,
        )

    elif column.constant is not None:
        dt.validate(df[column.name], column.constant)

    elif column.constant_list:
        dt.validate.subset(
            df[column.name],
            set([int(value) for value in column.constant_list]),
        )

    elif column.global_constant_list:
        dt.validate.subset(
            df[column.name],
            set([int(value) for value in column.global_constant_list.data]),
        )

    elif column.functional_dependency:
        if column.functional_dependency_use_mode == FDUseMode.GENERATE_FROM_KEYS:
            dt.validate.subset(
                df[column.name],
                set([int(value[0]) for value in column.functional_dependency.keys]),
            )

        elif column.functional_dependency_use_mode == FDUseMode.CHOOSE_FROM_VALUES:
            dt.validate.subset(
                df[column.name],
                set(
                    [
                        int(value[column.functional_dependency_value_position])
                        for value in column.functional_dependency.data.values()
                    ]
                ),
            )
    else:
        logging_info(f"No method-based validation applied to column {column.name}")
