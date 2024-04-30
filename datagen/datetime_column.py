"""
Column of datetime type
Different logic for date and datetime
"""

import datetime
import random as rnd
from .column import Column
from .const import (
    DatetimeGranularity,
    ChooseMethod,
    ColumnType,
    DATAGEN_VALIDATE_ERROR,
    DATAGEN_RUNTIME_ERROR,
)
from .utils import (
    logging_error,
    logging_info,
    generate_constant_list_value,
    generate_global_constant_list_value,
    generate_functional_dependency_value,
)
from .global_structuries import GlobalStructs
from dateutil.relativedelta import relativedelta

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class DatetimeColumn(Column):
    """
    Datetime column definition and methods
    """

    def __init__(self, column: dict, dataset, p_global_structs: GlobalStructs):
        """
        :param column: parsed from config dict structure containing column attributes
        :param dataset: parsed from config dict structure containing dataset attributes
        :param p_global_structs: class with global structures (FDs and constant lists)

        :attribute date_kind: datetime or date
        :attribute sequence_start_value: start value for sequence generation
        :attribute sequence_increment_by: sequence step size
        :attribute sequence_granularity: sequence step type
        :attribute constant: constant in case of constant generation
        :attribute datetime_set_max_datetime: max datetime in case of choosing from datetime set
        :attribute datetime_set_min_datetime: min datetime in case of choosing from datetime set
        :attribute datetime_set_granularity_type: datetime set granularity type
        :attribute datetime_set_granularity_value: granules number for creating datetime set
        :attribute datetime_set_choose_method: method of choosing from datetime set
        """
        super().__init__(column, dataset)

        logging_info(f"Datagen info: DatetimeColumn {self.name} initialization started.")

        self.super_generation_init(p_global_structs)
        self.super_validate()

        self.date_kind: ColumnType = ColumnType(column.get("type"))

        self.sequence_start_value: str = column.get("sequence", {}).get("start_value")
        self.sequence_increment_by: int = column.get("sequence", {}).get("increment_by")
        self.sequence_granularity: str = column.get("sequence", {}).get("granularity")
        self.sequence_current_value: str = None

        self.constant: str = column.get("constant")

        column_set_type = ""
        column_set_max_name = ""
        column_set_min_name = ""
        if self.date_kind == ColumnType.DATETIME:
            column_set_type = "datetime_set"
            column_set_max_name = "max_datetime"
            column_set_min_name = "min_datetime"
        elif self.date_kind == ColumnType.DATE:
            column_set_type = "date_set"
            column_set_max_name = "max_date"
            column_set_min_name = "min_date"

        self.datetime_set_max_datetime: str = column.get(column_set_type, {}).get(
            column_set_max_name
        )
        self.datetime_set_min_datetime: str = column.get(column_set_type, {}).get(
            column_set_min_name
        )
        self.datetime_set_granularity_type: str = column.get(column_set_type, {}).get(
            "granularity_type"
        )
        self.datetime_set_granularity_value: int = column.get(column_set_type, {}).get(
            "granularity_value"
        )
        self.datetime_set_choose_method: str = column.get(column_set_type, {}).get(
            "choose_method"
        )
        self.datetime_set_current_idx = 0
        self.datetime_set_max_idx = 0

        self.generation_init()
        self.validate()

        logging_info(f"Datagen info: DatetimeColumn {self.name} initialization ended.")

    def str_to_date(self, value: str) -> datetime.datetime:
        """
        Transform string date to datetime.datetime
        After reading from config we need to perform transformations
        :param value: input date as string
        :return:
        """
        try:
            if value and self.date_kind == ColumnType.DATETIME:
                return datetime.datetime.strptime(value, DATETIME_FORMAT)
            if value and self.date_kind == ColumnType.DATE:
                return datetime.datetime.strptime(value, DATE_FORMAT)
        except ValueError:
            logging_error(
                f"{DATAGEN_VALIDATE_ERROR}Can't recognize datetime format for {value} value."
            )

    def date_to_str(self, date: datetime.datetime) -> str:
        """
        Transform datetime.datetime date to string
        After transformations before writing data to disc
        :param date:
        :return:
        """
        try:
            if self.date_kind == ColumnType.DATETIME:
                return datetime.datetime.strftime(date, DATETIME_FORMAT)
            if self.date_kind == ColumnType.DATE:
                return datetime.datetime.strftime(date, DATE_FORMAT)
        except ValueError:
            logging_error(
                f"{DATAGEN_RUNTIME_ERROR}Can't recognize date_kind for column {self.name}."
            )

    def generation_init(self):
        """
        Preparing attributes for generating
        :return:
        """
        if self.sequence_granularity:
            self.sequence_start_value = self.str_to_date(self.sequence_start_value)
            self.sequence_granularity = DatetimeGranularity(self.sequence_granularity)
            self.sequence_current_value = self.sequence_start_value

        if self.constant:
            self.constant: datetime.datetime = self.str_to_date(self.constant)

        if self.datetime_set_granularity_type:
            self.datetime_set_choose_method = ChooseMethod(
                self.datetime_set_choose_method
            )
            self.datetime_set_max_datetime: datetime.datetime = self.str_to_date(
                self.datetime_set_max_datetime
            )
            self.datetime_set_min_datetime: datetime.datetime = self.str_to_date(
                self.datetime_set_min_datetime
            )
            self.datetime_set_granularity_type = DatetimeGranularity(
                self.datetime_set_granularity_type
            )
            # why not use month and year for datetime set?
            # because it's hard to say how many years/months are between two datetime values
            datetiff = self.datetime_set_max_datetime - self.datetime_set_min_datetime
            diff_seconds = int(datetiff.total_seconds())
            if self.datetime_set_granularity_type == DatetimeGranularity.SECOND:
                self.datetime_set_max_idx = (
                    diff_seconds // self.datetime_set_granularity_value
                )
            if self.datetime_set_granularity_type == DatetimeGranularity.MINUTE:
                self.datetime_set_max_idx = (
                    diff_seconds // 60
                ) // self.datetime_set_granularity_value
            if self.datetime_set_granularity_type == DatetimeGranularity.HOUR:
                self.datetime_set_max_idx = (
                    diff_seconds // (60 * 60)
                ) // self.datetime_set_granularity_value
            if self.datetime_set_granularity_type == DatetimeGranularity.DAY:
                self.datetime_set_max_idx = (
                    diff_seconds // (60 * 60 * 24)
                ) // self.datetime_set_granularity_value

        if self.constant_list_choose_method:
            self.constant_list = [
                self.str_to_date(value) for value in self.constant_list
            ]

    def validate(self):
        """
        Validating attributes with rules
        :return:
        """
        if self.datetime_set_max_datetime:
            if self.datetime_set_min_datetime > self.datetime_set_max_datetime:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In dataset {self.dataset.name} in column {self.name} "
                    f"min_date={self.datetime_set_min_datetime} greater than "
                    f"max_date={self.datetime_set_max_datetime}."
                )

    def generate(self) -> str:
        """
        Generate column value based on generation method
        :return:
        """

        if self.sequence_start_value:
            generated_value = self.sequence_current_value
            if self.sequence_granularity == DatetimeGranularity.SECOND:
                self.sequence_current_value += datetime.timedelta(
                    seconds=self.sequence_increment_by
                )
            if self.sequence_granularity == DatetimeGranularity.MINUTE:
                self.sequence_current_value += datetime.timedelta(
                    minutes=self.sequence_increment_by
                )
            if self.sequence_granularity == DatetimeGranularity.HOUR:
                self.sequence_current_value += datetime.timedelta(
                    seconds=self.sequence_increment_by
                )
            if self.sequence_granularity == DatetimeGranularity.DAY:
                self.sequence_current_value += datetime.timedelta(
                    days=self.sequence_increment_by
                )
            if self.sequence_granularity == DatetimeGranularity.MONTH:
                self.sequence_current_value += relativedelta(
                    months=self.sequence_increment_by
                )
            if self.sequence_granularity == DatetimeGranularity.YEAR:
                self.sequence_current_value += relativedelta(
                    years=self.sequence_increment_by
                )

            return self.date_to_str(generated_value)

        elif self.constant:
            return self.date_to_str(self.constant)

        elif self.constant_list:
            return self.date_to_str(generate_constant_list_value(self))

        elif self.global_constant_list:
            return generate_global_constant_list_value(self)

        elif self.datetime_set_max_datetime:
            if self.datetime_set_choose_method == ChooseMethod.RANDOM:
                granules_cnt = (
                    rnd.randint(0, self.datetime_set_max_idx)
                    * self.datetime_set_granularity_value
                )
            if self.datetime_set_choose_method == ChooseMethod.ROUND_ROBIN:
                granules_cnt = (
                    self.datetime_set_current_idx * self.datetime_set_granularity_value
                )
                self.datetime_set_current_idx = (
                    self.datetime_set_current_idx + 1
                ) % self.datetime_set_max_idx

            if self.datetime_set_granularity_type == DatetimeGranularity.SECOND:
                return self.date_to_str(
                    self.datetime_set_min_datetime
                    + datetime.timedelta(seconds=granules_cnt)
                )
            if self.datetime_set_granularity_type == DatetimeGranularity.MINUTE:
                return self.date_to_str(
                    self.datetime_set_min_datetime
                    + datetime.timedelta(minutes=granules_cnt)
                )
            if self.datetime_set_granularity_type == DatetimeGranularity.HOUR:
                return self.date_to_str(
                    self.datetime_set_min_datetime
                    + datetime.timedelta(hours=granules_cnt)
                )
            if self.datetime_set_granularity_type == DatetimeGranularity.DAY:
                return self.date_to_str(
                    self.datetime_set_min_datetime
                    + datetime.timedelta(days=granules_cnt)
                )

        elif self.functional_dependency:
            return generate_functional_dependency_value(self)

        else:
            logging_error(
                f"{DATAGEN_RUNTIME_ERROR}In dataset {self.dataset.name} in column {self.name} "
                f"can't choose generating method"
            )
