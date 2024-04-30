"""
Column of number type
Initialization, validation, generation methods
"""

import random as rnd
import math
from .column import Column
from .utils import (
    logging_error,
    logging_info,
    generate_constant_list_value,
    generate_global_constant_list_value,
    generate_functional_dependency_value,
)
from .const import ChooseMethod, DATAGEN_VALIDATE_ERROR, DATAGEN_RUNTIME_ERROR
from .global_structuries import GlobalStructs


class NumberColumn(Column):
    """
    Class of number column
    """

    def __init__(self, column: dict, dataset, p_global_structs: GlobalStructs):
        """
        :param column: parsed from config dict structure containing column attributes
        :param dataset: parsed from config dict structure containing dataset attributes
        :param p_global_structs: class with global structures (FDs and constant lists)

        :attribute sequence_start_value: start value for sequence generation
        :attribute sequence_increment_by: sequence step size
        :attribute constant: constant in case of constant generation
        :attribute number_set_max_number: max number in case of choosing from datetime set
        :attribute number_set_min_number: min number in case of choosing from datetime set
        :attribute number_set_granularity_type: number set granularity type
        :attribute number_set_choose_method: method of choosing from number set
        """
        super().__init__(column, dataset)

        logging_info(f"Datagen info: NumberColumn {self.name} initialization started.")

        self.super_generation_init(p_global_structs)
        self.super_validate()

        self.sequence_start_value: int = column.get("sequence", {}).get("start_value")
        self.sequence_increment_by: int = column.get("sequence", {}).get(
            "increment_by", 1
        )
        self.sequence_current_value = None

        self.constant = column.get("constant")

        self.number_set_max_number: int = column.get("number_set", {}).get("max_number")
        self.number_set_min_number: int = column.get("number_set", {}).get("min_number")
        self.number_set_granularity: int = column.get("number_set", {}).get(
            "granularity", 1
        )
        self.number_set_choose_method: str = column.get("number_set", {}).get(
            "choose_method"
        )
        self.number_set_current_idx = 0

        self.validate()
        self.generation_init()

        logging_info(f"Datagen info: NumberColumn {self.name} initialization ended.")

    def validate(self):
        """
        Validation of attributes by rules
        :return:
        """
        # Here we compare number with None exactly by is/not, because number 0 is false
        if self.number_set_min_number is not None:
            number_set_granularity = 1
            if self.number_set_granularity is not None:
                number_set_granularity = self.number_set_granularity
            if self.number_set_min_number > self.number_set_max_number:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In dataset {self.dataset.name} in column {self.name} "
                    f"min_number={self.number_set_min_number} greater than max_number={self.number_set_max_number}."
                )
            # ceil here for distinguishing 0 and 1 granule cases
            if (
                math.ceil(self.number_set_min_number / number_set_granularity)
                > self.number_set_max_number // number_set_granularity
            ):
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In dataset {self.dataset.name} in column {self.name} "
                    f"can't create correct interval of values "
                    f"for min_number={self.number_set_min_number}, "
                    f"max_number={self.number_set_max_number}, "
                    f"granularity={number_set_granularity}."
                )

    def generation_init(self):
        """
        Transformation of attributes in order to prepare for generation
        :return:
        """
        if self.sequence_start_value is not None:
            self.sequence_current_value: int = self.sequence_start_value
            if self.name in self.dataset.state:
                self.sequence_current_value: int = self.dataset.state.get(self.name)

        if self.number_set_min_number is not None:
            if self.number_set_granularity is None:
                self.number_set_granularity = 1
            self.number_set_min_number: int = math.ceil(
                self.number_set_min_number / self.number_set_granularity
            )
            self.number_set_max_number: int = (
                self.number_set_max_number // self.number_set_granularity
            )
            self.number_set_current_idx = self.number_set_min_number
            self.number_set_choose_method: ChooseMethod = ChooseMethod(
                self.number_set_choose_method
            )

    def generate(self) -> int:
        """
        Generation in according to different methods
        :return: generated value
        """

        if self.sequence_start_value is not None:
            generated_value = self.sequence_current_value
            self.sequence_current_value += self.sequence_increment_by
            # for saving state in state file
            self.dataset.state[self.name] = generated_value + self.sequence_increment_by
            return generated_value

        elif self.constant is not None:
            return self.constant

        elif self.constant_list:
            return generate_constant_list_value(self)

        elif self.global_constant_list:
            return generate_global_constant_list_value(self)

        elif self.number_set_min_number is not None:
            idx = None
            if self.number_set_choose_method == ChooseMethod.RANDOM:
                return (
                    rnd.randint(self.number_set_min_number, self.number_set_max_number)
                    * self.number_set_granularity
                )
            if self.number_set_choose_method == ChooseMethod.ROUND_ROBIN:
                idx = self.number_set_current_idx
                self.number_set_current_idx = (
                    self.number_set_current_idx + 1
                ) % self.number_set_max_number
                return idx * self.number_set_granularity

        elif self.functional_dependency:
            return generate_functional_dependency_value(self)

        else:
            logging_error(
                f"{DATAGEN_RUNTIME_ERROR}In dataset {self.dataset.name} in column {self.name} "
                f"can't choose generating method"
            )

