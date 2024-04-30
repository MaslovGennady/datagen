"""
Functional dependency - structure that implements key-value logic
"""

import csv
import os
from typing import Tuple, List
from .utils import logging_error, logging_info
from .const import DATAGEN_VALIDATE_ERROR, DATAGEN_RUNTIME_ERROR


class FunctionalDependency:
    """
    Attributes and methods of FD
    """

    def __init__(self, functional_dependency: dict):
        """
        :param functional_dependency: parsed from config dict structure containing functional_dependency attributes

        :attribute name: name of functional_dependency
        :attribute separator: character to use as separator when parse separated values
        :attribute key_columns: list ids of columns that will be treated as keys of FD
        :attribute data_columns: list ids of columns that will be treated as data of FD
        :attribute file: path to file with values
        :attribute data: key-value structure for getting FD data by key
        :attribute keys: list of FD keys for choosing between them
        """
        self.name: str = functional_dependency.get("name").lower()

        logging_info(f"Datagen info: FunctionalDependency {self.name} initialization started.")

        self.separator: str = functional_dependency.get("separator", ',')
        self.key_columns: List[int] = functional_dependency.get("key_columns")
        self.data_columns: List[int] = functional_dependency.get("data_columns")
        self.file: str = functional_dependency.get("file")
        self.data: dict = {}
        self.keys: list = []
        self.keys_cnt: int = 0

        self.key_length: int = len(self.key_columns)
        self.data_length: int = len(self.data_columns)

        self.validate()
        self.data_init()

        logging_info(f"Datagen info: FunctionalDependency {self.name} initialization ended.")

    def validate(self):
        """
        Validate by rules
        :return:
        """
        for value in self.key_columns:
            if value < 0:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}column numbers from key_columns attribute "
                    f"of {self.name} functional dependency must be positive"
                )

        for value in self.data_columns:
            if value < 0:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}column numbers from data_columns attribute "
                    f"of {self.name} functional dependency nust be positive"
                )

        if len(set(self.key_columns).intersection(set(self.data_columns))):
            logging_error(
                f"{DATAGEN_VALIDATE_ERROR}key_columns and data_columns lists must have nothing in common"
            )

        if not os.path.exists(self.file):
            logging_error(
                f"{DATAGEN_VALIDATE_ERROR}file={self.file} from file attribute "
                f"of functional_dependency={self.name} not exists"
            )

    def data_init(self):
        """
        Initializing of key-value structure
        :return:
        """
        with open(self.file, newline="\n") as csvfile:
            reader = csv.reader(csvfile,
                                delimiter=self.separator)
            data_length = 0
            row_number = 0
            for row in reader:
                data_length = len(row)
                if (
                    data_length < self.key_length + self.data_length
                    or data_length < max(self.key_columns)
                    or data_length < max(self.data_columns)
                ):
                    logging_error(
                        f"{DATAGEN_VALIDATE_ERROR}length of data ({data_length}) "
                        f"for functional_dependency={self.name} "
                        f"in file={self.file} "
                        f"in row with number={row_number} "
                        f"isn't enough for functional_dependency key_columns={str(self.key_columns)} "
                        f"and data_columns={str(self.data_columns)}"
                    )

                row_number += 1

                key = [str(row[i]) for i in self.key_columns]
                key = tuple(key)
                self.keys.append(key)
                self.keys_cnt += 1
                self.data[key] = [row[i] for i in self.data_columns]

    def get_key_by_idx(self, idx: int):
        """
        Getting value from keys of FD
        :param idx: number of key in keys list
        :return:
        """
        if 0 <= idx <= self.keys_cnt - 1:
            return self.keys[idx][0]
        else:
            logging_error(
                f"{DATAGEN_RUNTIME_ERROR}No key with index={idx} in functional dependency={self.name}"
            )

    def get_value_by_key(self, key: Tuple[str], value_position: int):
        """
        Getting value by key of FD
        :param key: tuple of key columns
        :param value_position: position of returning value in data attributes list
        :return:
        """
        return self.data.get(key)[value_position]
