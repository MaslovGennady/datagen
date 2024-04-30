"""
Global structures that can be used in generation in all datasets
"""

from .functional_dependency import FunctionalDependency
from .constant_list import ConstantList
from .utils import logging_info
from typing import Dict


class GlobalStructs:
    """
    Class containing all global structures
    """

    _instance = None

    def __new__(cls, config: dict):
        if not cls._instance:

            logging_info("Datagen info: GlobalStructs initialization started.")

            cls._instance = super(GlobalStructs, cls).__new__(cls)

            cls._instance.constant_lists: Dict[str, ConstantList] = {}
            cls._instance.functional_dependencies: Dict[str, FunctionalDependency] = {}

            for constant_list in config.get("constant_lists", []):
                cl = ConstantList(constant_list)
                cls._instance.constant_lists[cl.name] = cl

            for functional_dependency in config.get("functional_dependencies", []):
                fd = FunctionalDependency(functional_dependency)
                cls._instance.functional_dependencies[fd.name] = fd

            logging_info("Datagen info: GlobalStructs initialization ended.")

        return cls._instance
