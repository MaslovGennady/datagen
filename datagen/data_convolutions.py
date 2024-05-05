"""
Data convolution - structure that contains data in collapsed format
"""

import csv
import os
from typing import Tuple, List, Any
from .utils import logging_error, logging_info
from .const import DATAGEN_VALIDATE_ERROR, DATAGEN_RUNTIME_ERROR


class DataConvolution:
    """
    Attributes and methods of DC
    """

    def __init__(self, data_convolution: dict):
        """
        :param data_convolution: parsed from config dict structure containing functional_dependency attributes

        :attribute name: name of functional_dependency
        :attribute separator: character to use as separator when parse separated values
        :attribute file: path to file with values
        :attribute data: key-value structure for getting FD data by key
        """
        self.name: str = data_convolution.get("name").lower()

        logging_info(f"Datagen info: DataConvolution {self.name} initialization started.")

        self.separator: str = data_convolution.get("separator", ',')
        self.file: str = data_convolution.get("file")
        self.data: List[List[Any[str, int]]] = []

        self.validate()
        self.data_init()

        logging_info(f"Datagen info: DataConvolution {self.name} initialization ended.")

    def validate(self):
        """
        Validate by rules
        :return:
        """

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
