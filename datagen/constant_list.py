"""
Constant list definition
"""

import os
from .utils import logging_error, logging_info
from .const import DATAGEN_RUNTIME_ERROR, DATAGEN_VALIDATE_ERROR


class ConstantList:
    """
    Defines a set of constant values and methods of init and getting them
    """

    def __init__(self, constant_list: dict):
        """
        :param constant_list: parsed from config dict structure containing constant_list attributes

        :attribute name: name of constant list
        :attribute data: list of values
        :attribute file: path to file with values
        """

        self.name: str = constant_list.get("name").lower()

        logging_info(f"Datagen info: ConstantList {self.name} initialization started.")

        self.data: list[str] = constant_list.get("data", [])
        self.file: str = constant_list.get("file", "")
        self.data_length: int = 0

        self.validate()
        self.generation_init()

        logging_info(f"Datagen info: ConstantList {self.name} initialization ended.")

    def validate(self):
        """
        Validating attributes of structure
        :return:
        """
        if self.file != "" and not os.path.exists(self.file):
            logging_error(
                f"{DATAGEN_VALIDATE_ERROR}file={self.file} from file attribute of constant_list not exists."
            )

    def generation_init(self):
        """
        Preparing attributes for using in generations
        :return:
        """
        data_length = 0
        if self.data:
            data_length = len(self.data)

        if not self.data and self.file is not None:
            with open(self.file) as f:
                for line in f:
                    self.data.append(line.strip("\n"))
                    data_length += 1

        self.data_length = data_length

    def get_value_by_id(self, idx: int):
        """
        Getting value from constant list
        :param idx: index of value in constant list
        :return: constant list element
        """
        if 0 <= idx <= self.data_length - 1:
            return self.data[idx]
        else:
            logging_error(
                f"{DATAGEN_RUNTIME_ERROR}No data with index={idx} in constant list={self.name}"
            )
