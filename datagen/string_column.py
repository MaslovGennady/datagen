"""
String column
Initialization, validation, generation methods
"""

from .column import Column
from .utils import (
    logging_error,
    logging_info,
    generate_constant_list_value,
    generate_global_constant_list_value,
    generate_functional_dependency_value,
)
from .const import DATAGEN_VALIDATE_ERROR, DATAGEN_RUNTIME_ERROR
from .global_structuries import GlobalStructs
import string
import random as rnd
import uuid


class StringColumn(Column):
    """
    Class of string column
    """

    def __init__(self, column: dict, dataset, p_global_structs: GlobalStructs):
        """
        :param column: parsed from config dict structure containing column attributes
        :param dataset: parsed from config dict structure containing dataset attributes
        :param p_global_structs: class with global structures (FDs and constant lists)

        :attribute constant: constant in case of constant generation
        :attribute random_digits_length: length of random digits value that will be generated
        :attribute random_letters_length: length of random letters value that will be generated
        """
        super().__init__(column, dataset)

        logging_info(f"Datagen info: StringColumn {self.name} initialization started.")

        self.super_generation_init(p_global_structs)
        self.super_validate()

        self.constant: str = column.get("constant")

        self.random_digits_length: int = column.get("random_digits_length")
        self.random_letters_length: int = column.get("random_letters_length")

        self.uuid: str = column.get("uuid")

        self.validate()

        logging_info(f"Datagen info: StringColumn {self.name} initialization ended.")

    def validate(self):
        """
        Validation of attributes by rules
        :return:
        """
        if self.random_letters_length and self.random_letters_length <= 0:
            logging_error(
                f"{DATAGEN_VALIDATE_ERROR}In dataset {self.dataset.name} in column {self.name} "
                f"random_letters_length <= 0"
            )

        if self.random_digits_length and self.random_digits_length <= 0:
            logging_error(
                f"{DATAGEN_VALIDATE_ERROR}In dataset {self.dataset.name} in column {self.name} "
                f"random_digits_length <= 0"
            )

        if self.jinja_template:
            try:
                self.jinja_template.render({})
            except Exception as e:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In dataset {self.dataset.name} in column {self.name} "
                    f"jinja template is not valid",
                    e
                )

    def generate(self) -> str:
        """
        Generation in according to different methods
        :return: generated value
        """

        if self.constant:
            return self.constant

        elif self.constant_list:
            return generate_constant_list_value(self)

        elif self.global_constant_list:
            return generate_global_constant_list_value(self)

        elif self.functional_dependency:
            return generate_functional_dependency_value(self)

        elif self.random_letters_length:
            letters = string.ascii_lowercase
            return "".join(
                rnd.choice(letters) for i in range(self.random_letters_length)
            )

        elif self.random_digits_length:
            digits = string.digits
            return "".join(rnd.choice(digits) for i in range(self.random_digits_length))

        elif self.uuid:
            return uuid.uuid4()

        elif self.jinja_template:
            logging_info(self.dataset.row)
            return self.jinja_template.render(**self.dataset.row)

        else:
            logging_error(
                f"{DATAGEN_RUNTIME_ERROR}In dataset {self.dataset.name} in column {self.name} "
                f"can't choose generating method"
            )
