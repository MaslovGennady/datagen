"""
Class that represents dataset
"""

from __future__ import annotations

import os
import json
import csv

from datetime import datetime
from typing import Any, List

from .utils import logging_error, logging_info
from .data_convolution import DataConvolution
from .number_column import NumberColumn
from .string_column import StringColumn
from .datetime_column import DatetimeColumn
from .const import ColumnType, WriteMethod, FDUseMode, DATAGEN_VALIDATE_ERROR, DATAGEN_RUNTIME_ERROR
from .global_structuries import GlobalStructs


class Dataset:
    """
    Attributes and methods for generating data
    """

    def __init__(self, dataset: dict, p_global_structs: GlobalStructs, state: dict):
        """
        :param dataset: parsed from config dict structure containing dataset attributes
        :param p_global_structs: class with global structures (FDs and constant lists)
        :param state: dict with last generation state

        :attribute row: dict
        :attribute rows: list of all data in case we need to sort it before writing to disc
        :attribute name: name of dataset
        :attribute state: state of generation (starting values for sequence columns)
        :attribute columns: column definitions list
        :attribute row_count: number of rows to generate
        :attribute order_by: order by columns list
        :attribute separator: separator symbol for data file
        :attribute quote_values: quote values in result file or not
        :attribute write_method: column definitions list
        :attribute data_convolution_name: name of DC that will be used for generation
        :attribute data_convolution: link to actual DC object that will be used for generation
        :attribute data_convolution_value_position: position of value in DC row
        """

        self.name: str = dataset.get("name").lower()

        logging_info(f"Datagen info: Dataset {self.name} initialization started.")

        self.row: dict = {}
        self.rows: List[List[Any[str | int]]] = []

        self.state: dict = state

        self.columns: List[Any[NumberColumn | DatetimeColumn | StringColumn]] = []
        for column in dataset.get("columns"):
            column_type = ColumnType(column.get("type").lower())
            if column_type == ColumnType.NUMBER:
                nc = NumberColumn(column, self, p_global_structs)
                self.columns.append(nc)

            elif column_type in (ColumnType.DATETIME, ColumnType.DATE):
                dc = DatetimeColumn(column, self, p_global_structs)
                self.columns.append(dc)

            elif column_type == ColumnType.STRING:
                sc = StringColumn(column, self, p_global_structs)
                self.columns.append(sc)

        self.row_count: int = dataset.get("row_count")
        self.order_by: List[str] = [col.lower() for col in dataset.get("order_by", [])]
        self.separator: str = dataset.get("separator")
        self.quote_values: int = dataset.get("quote_values")
        self.write_method: str = dataset.get("write_method")
        if self.write_method:
            self.write_method = WriteMethod(self.write_method.lower())

        self.data_convolution: DataConvolution = None
        self.data_convolution_name: str = dataset.get("data_convolution_name", "").lower()

        self.generation_init(p_global_structs)
        self.validate(p_global_structs)

        logging_info(f"Datagen info: Dataset {self.name} initialization ended.")

    def generation_init(self, p_global_structs):
        """
        Transform of class attributes, prepare for generating
        :param p_global_structs: common data structures
        :return:
        """
        if self.data_convolution_name:
            if (
                self.data_convolution_name
                in p_global_structs.data_convolutions
            ):
                self.data_convolution = p_global_structs.data_convolutions[
                    self.data_convolution_name
                ]
            else:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}Data convolution {self.data_convolution_name} not found in "
                    f"data_convolutions section of config. Dataset={self.name}"
                )

    def validate(self, p_global_structs: GlobalStructs):
        """
        Validation with specific rules
        :return:
        """
        # Default values just to validate jinjas
        jinja_column_defaults = {}
        for column in self.columns:
            if column.__class__.__name__ == "DatetimeColumn":
                jinja_column_defaults[column.name] = '2024-12-12'
            elif column.__class__.__name__ == "NumberColumn":
                jinja_column_defaults[column.name] = '1'
            elif column.__class__.__name__ == "StringColumn":
                jinja_column_defaults[column.name] = '1'
            else:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In dataset {self.name} in column {column.name} "
                    f"unknown column type {column.__class__.__name__}"
                )

        for column in self.columns:

            tmp_column = column

            if column.dataset_columns_as_fd_key:

                all_fds = p_global_structs.functional_dependencies
                fd = all_fds[column.functional_dependency_name]

                for fd_key_column in column.dataset_columns_as_fd_key:
                    if fd_key_column not in [column.name for column in self.columns]:
                        logging_error(
                            f"{DATAGEN_VALIDATE_ERROR}In dataset {self.name} in column {tmp_column.name} "
                            f"in dataset_columns_as_fd_key attribute value {fd_key_column} "
                            f"not found in dataset column list names."
                        )

            if column.jinja_template:
                try:
                    # Render for validation
                    column.jinja_template.render(**jinja_column_defaults)
                except Exception as e:
                    logging_error(
                        f"{DATAGEN_VALIDATE_ERROR}In dataset {self.name} in column {tmp_column.name} "
                        f"jinja template is not valid",
                        e
                    )

            if column.data_convolution_value_position is not None and not self.data_convolution:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In dataset {self.name} in column {tmp_column.name} "
                    f"data_convolution_value_position attribute filled, "
                    f"but no data_convolution_name given in dataset options."
                )

            if self.data_convolution:
                # Subtract 1 from data_length for the fact that data_length is a len() of DC row
                # but data_convolution_value_position starts from 0
                # And another subtraction of 1 for the fact that the last element of DC row is s number of rows
                if (
                    column.data_convolution_value_position is not None and
                    column.data_convolution_value_position > self.data_convolution.data_length - 2
                ):
                    logging_error(
                        f"{DATAGEN_VALIDATE_ERROR}In column {column.name} "
                        f"value_position {column.data_convolution_value_position} for "
                        f"data convolution {self.data_convolution_name} is too big."
                    )

        if self.order_by:
            for column in self.order_by:
                column_name = column
                if column_name not in [column.name for column in self.columns]:
                    logging_error(
                        f"{DATAGEN_VALIDATE_ERROR}In dataset {self.name} in order_by list column={column_name} "
                        f"not exists in dataset columns list"
                    )

        if self.order_by:
            if len(self.order_by) != len(list(dict.fromkeys(self.order_by))):
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In dataset {self.name} in order_by list duplicate column names found"
                )

        column_names = [column.name for column in self.columns]
        if len(column_names) != len(list(dict.fromkeys(column_names))):
            logging_error(
                f"{DATAGEN_VALIDATE_ERROR}In dataset {self.name} in columns list duplicate column names found"
            )

    def get_file_descriptor(self, out_dir: os.path):
        """
        Getting file descriptor of output file for data generation of this dataset
        :param out_dir: destination to datasets
        :return:
        """
        output_file_name = os.path.join(out_dir, self.name)
        file_open_regime = "w"
        if not self.write_method or self.write_method == WriteMethod.OVERWRITE:
            file_open_regime = "w"
        elif self.write_method == WriteMethod.APPEND:
            file_open_regime = "a"
        elif self.write_method == WriteMethod.NEW:
            file_open_regime = "w"
            filename_time_suffix = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            file_name_suffix = f"{self.name}_{filename_time_suffix}"
            output_file_name = os.path.join(out_dir, file_name_suffix)

        return open(output_file_name, file_open_regime, newline="")

    def get_file_csv_writer(self, csvfile) -> csv.writer:
        """
        Get csv writer object with file descriptor
        :param csvfile:
        :return:
        """
        return csv.writer(
            csvfile,
            delimiter=self.separator if self.separator else ",",
            quotechar='"',
            quoting=(
                csv.QUOTE_ALL
                if self.quote_values and self.quote_values == 1
                else csv.QUOTE_NONE
            ),
        )

    def generate_data(self, writer: csv.writer):
        """
        Generating data
        Writing data without sorting
        Saving data to dataset class in case sorting needed
        :param writer: csv writer object
        :return:
        """

        logging_info(f"Datagen info: Dataset {self.name} generate_data started.")

        first_priority_generation_cols = []
        second_priority_generation_cols = []
        third_priority_generation_cols = []

        for column in self.columns:
            if not (
                    column.functional_dependency
                    and column.functional_dependency_use_mode
                    == FDUseMode.CHOOSE_FROM_VALUES
            ) and not column.jinja_template:
                first_priority_generation_cols.append(column)
            elif (
                    column.functional_dependency
                    and column.functional_dependency_use_mode
                    == FDUseMode.CHOOSE_FROM_VALUES
            ):
                second_priority_generation_cols.append(column)
            else:
                third_priority_generation_cols.append(column)

        generation_order = [first_priority_generation_cols,
                            second_priority_generation_cols,
                            third_priority_generation_cols]

        if self.row_count:

            for i in range(self.row_count):

                for priority_columns in generation_order:

                    try:
                        generating_column = ''
                        for column in priority_columns:
                            generating_column = column.name
                            self.row[column.name] = column.generate()

                    except Exception as e:
                        logging_error(
                            f"{DATAGEN_RUNTIME_ERROR}Error occured while generation column={generating_column}: ",
                            e
                        )

                if not self.order_by:
                    writer.writerow([self.row.get(column.name) for column in self.columns])
                else:
                    self.rows.append([self.row.get(column.name) for column in self.columns])

        elif self.data_convolution:

            for dc_row in self.data_convolution.data:

                for i in range(int(dc_row[-1])):

                    for priority_columns in generation_order:

                        try:
                            generating_column = ''
                            for column in priority_columns:
                                generating_column = column.name
                                if column.data_convolution_value_position is not None:
                                    self.row[column.name] = dc_row[column.data_convolution_value_position]
                                else:
                                    self.row[column.name] = column.generate()

                        except Exception as e:
                            logging_error(
                                f"{DATAGEN_RUNTIME_ERROR}Error occured while generation "
                                f"column={generating_column}: ",
                                e
                            )

                    if not self.order_by:
                        writer.writerow([self.row.get(column.name) for column in self.columns])
                    else:
                        self.rows.append([self.row.get(column.name) for column in self.columns])

        logging_info(f"Datagen info: Dataset {self.name} generate_data ended.")

    def get_sort_columns_ids(self) -> list[int]:
        """
        Getting order_by section column ids in dataset columns
        :return: list of ids
        """
        sort_columns_ids = []
        if self.order_by:
            for order_by_column in self.order_by:
                for column_idx, column in enumerate(self.columns):
                    if column.name == order_by_column:
                        sort_columns_ids.append(column_idx)
        return sort_columns_ids

    def write_sorted_data(self, writer: csv.writer, sort_columns_ids: list[int]):
        """
        Writing sorted data in case of order_by section is not empty
        :param writer: csv writer object
        :param sort_columns_ids: list of order_by columns ids
        :return:
        """

        logging_info(f"Datagen info: Dataset {self.name} write_sorted_data started.")

        if sort_columns_ids:
            writer.writerows(
                sorted(
                    self.rows,
                    key=lambda x: [x[col_id] for col_id in sort_columns_ids],
                )
            )

        logging_info(f"Datagen info: Dataset {self.name} write_sorted_data ended.")

    def write_state(self, out_dir: os.path):
        """
        Writing state of generation
        :param out_dir: destination to output files
        :return:
        """
        if self.state:
            output_state_file_name = os.path.join(out_dir, f"{self.name}__state__")
            with open(output_state_file_name, "w") as state_file:
                state = json.dumps(self.state)
                state_file.write(state)

    def generate(self, out_dir: os.path):
        """
        Main function to generate dataset data
        :param out_dir: destination to output files
        :return:
        """

        logging_info(f"Datagen info: Dataset {self.name} generate started.")

        with self.get_file_descriptor(out_dir) as csvfile:
            writer = self.get_file_csv_writer(csvfile)
            self.generate_data(writer)
            sort_columns_ids = self.get_sort_columns_ids()
            self.write_sorted_data(writer, sort_columns_ids)
            self.write_state(out_dir)

        logging_info(f"Datagen info: Dataset {self.name} generate ended.")
