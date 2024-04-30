import datatest as dt

from datagen.const import FDUseMode
from .utils import is_valid_uuid
from datagen.utils import logging_info


def validate_string_column(df, column):
    """
    Part of testing script consisting of validation of string column in according to generate method
    :param df: dataset
    :param column: column class
    :return:
    """
    if column.constant:
        dt.validate(df[column.name], column.constant)

    elif column.constant_list:
        dt.validate.subset(df[column.name], set(column.constant_list))

    elif column.global_constant_list:
        dt.validate.subset(df[column.name], set(column.global_constant_list.data))

    elif column.functional_dependency:
        if column.functional_dependency_use_mode == FDUseMode.GENERATE_FROM_KEYS:
            dt.validate.subset(
                df[column.name],
                set([value[0] for value in column.functional_dependency.keys]),
            )

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

    elif column.random_letters_length:
        dt.validate.regex(
            df[column.name],
            "^[a-zA-Zа-яА-Я]{" + str(column.random_letters_length) + "}$",
        )

    elif column.random_digits_length:
        dt.validate.regex(
            df[column.name],
            "^[0-9]{" + str(column.random_digits_length) + "}$",
        )

    elif column.uuid:
        uuid_is_valid_col_name = f"{column.name}_valid"
        df[uuid_is_valid_col_name] = df[column.name].apply(is_valid_uuid)
        dt.validate(df[uuid_is_valid_col_name], True)
    else:
        logging_info(f"No method-based validation applied to column {column.name}")
