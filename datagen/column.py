"""
Column parent class
Other column classes inherit this class
"""

from jinja2 import Template

from .constant_list import ConstantList
from .functional_dependency import FunctionalDependency
from .utils import logging_error
from .const import ChooseMethod, FDUseMode, DATAGEN_VALIDATE_ERROR
from .global_structuries import GlobalStructs


class Column:
    """
    Class with common objects of all column classes
    """

    def __init__(self, column: dict, dataset):
        """
        :param column: parsed from config dict structure containing column attributes
        :param dataset: link to dataset class of this column

        :attribute functional_dependency_name: name of FD that will be used for generation
        :attribute functional_dependency: link to actual FD object that will be used for generation
        :attribute functional_dependency_use_mode: how to use FD: get one of keys of value by key
        :attribute dataset_columns_as_fd_key: list of columns to make up key for FD
        :attribute functional_dependency_value_position: position of value in FD data columns list
            to return as generated value
        :attribute functional_dependency_choose_method: how to choose value from set
        :attribute functional_dependency_current_idx: additional attribute
        :attribute jinja_template: jinja template
        """
        self.dataset = dataset
        self.name: str = column.get("name").lower()

        self.global_constant_list_name: str = (
            column.get("global_constant_list", {}).get("name", "").lower()
        )
        self.global_constant_list: ConstantList = None
        self.global_constant_list_choose_method: str = column.get(
            "global_constant_list", {}
        ).get("choose_method")
        self.global_constant_list_current_idx: int = 0

        self.constant_list_values_length: int = 0
        self.constant_list: str = column.get("constant_list", {}).get("data", [])
        self.constant_list_choose_method: str = column.get("constant_list", {}).get(
            "choose_method"
        )
        self.constant_list_current_idx: int = 0

        functional_dependency: dict = column.get("functional_dependency", {})
        self.functional_dependency_name: str = functional_dependency.get(
            "name", ""
        ).lower()
        self.functional_dependency: FunctionalDependency = None
        self.functional_dependency_use_mode: str = functional_dependency.get(
            "use_mode", ""
        ).lower()
        self.dataset_columns_as_fd_key: list[str] = [
            col.lower()
            for col in functional_dependency.get("dataset_columns_as_fd_key", [])
        ]
        self.functional_dependency_value_position: int = functional_dependency.get(
            "value_position", 0
        )
        self.functional_dependency_choose_method: str = functional_dependency.get(
            "choose_method"
        )
        self.functional_dependency_current_idx: int = 0

        self.jinja_template: str = column.get("jinja_template")

    def super_generation_init(self, p_global_structs: GlobalStructs):
        """
        Transform of class attributes, prepare for generating
        :param p_global_structs: common data structures
        :return:
        """
        if self.global_constant_list_name != "":
            if self.global_constant_list_name in p_global_structs.constant_lists:
                self.global_constant_list = p_global_structs.constant_lists[
                    self.global_constant_list_name
                ]
            else:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}Constant list {self.global_constant_list_name} not found in "
                    f"constant_lists section of config. Column={self.name}. Dataset={self.dataset.name}"
                )

            self.global_constant_list_choose_method: ChooseMethod = ChooseMethod(
                self.global_constant_list_choose_method
            )

        if self.functional_dependency_name != "":
            if (
                self.functional_dependency_name
                in p_global_structs.functional_dependencies
            ):
                self.functional_dependency = p_global_structs.functional_dependencies[
                    self.functional_dependency_name
                ]
            else:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}Functional dependency {self.functional_dependency_name} not found in "
                    f"functional_dependencies section of config. Column={self.name}. Dataset={self.dataset.name}"
                )
            if self.functional_dependency_choose_method:
                self.functional_dependency_choose_method: ChooseMethod = ChooseMethod(
                    self.functional_dependency_choose_method
                )
            self.functional_dependency_use_mode: FDUseMode = FDUseMode(
                self.functional_dependency_use_mode
            )

        if self.constant_list:
            self.constant_list_values_length = len(self.constant_list)
            self.constant_list_choose_method: ChooseMethod = ChooseMethod(
                self.constant_list_choose_method
            )

        if self.jinja_template:
            self.jinja_template = Template(self.jinja_template)

    def super_validate(self):
        """
        Validations of class attributes
        :return:
        """
        if self.functional_dependency:
            if (
                self.functional_dependency_value_position
                > self.functional_dependency.data_length - 1
            ):
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In column {self.name} "
                    f"value_position {self.functional_dependency_value_position} for "
                    f"functional dependency {self.functional_dependency.name} is too big."
                )

        if self.functional_dependency_use_mode == FDUseMode.GENERATE_FROM_KEYS:
            if self.functional_dependency.key_length > 1:
                logging_error(
                    f"{DATAGEN_VALIDATE_ERROR}In column {self.name} "
                    f"functional_dependency_use_mode is generate_from_keys but key for "
                    f"functional dependency {self.functional_dependency.name} is complex."
                )
