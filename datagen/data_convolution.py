"""
Data convolution - structure that contains data in collapsed format
"""

import csv
import os
from typing import List, Any
from .utils import logging_error, logging_info
from .const import DATAGEN_VALIDATE_ERROR


class DataConvolution:
    """
    Attributes and methods of DC
    """

    def __init__(self, data_convolution: dict):
        """
        :param data_convolution: parsed from config dict structure containing data_convolution attributes

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
        self.data_length: int = 0

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
                f"of data_convolution={self.name} not exists"
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
                if data_length == 0:
                    data_length = len(row)
                else:
                    if data_length != len(row):
                        logging_error(
                            f"{DATAGEN_VALIDATE_ERROR}number of elements of {row_number} row in data of "
                            f"{self.file} data_convolution differs from other rows."
                        )

                if not row[-1].isdigit() or int(row[-1]) < 0:
                    logging_error(
                        f"{DATAGEN_VALIDATE_ERROR}last element of {row_number} row in data of "
                        f"{self.file} data_convolution is not a positive number."
                        f"But it must be."
                    )

                row_number += 1
                self.data.append(list(row))

        self.data_length = data_length
