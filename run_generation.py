import argparse
import json
import logging
import os
from referencing import Registry
from referencing.jsonschema import DRAFT7
from jsonschema import ValidationError, Draft7Validator
from typing import List
from datagen.dataset import Dataset
from datagen.global_structuries import GlobalStructs
from datagen.utils import logging_error, logging_info, logging_warning
from datagen.const import DATAGEN_VALIDATE_ERROR


def prepare_validator() -> Draft7Validator:
    """
    Preparing json schema validator object
    :return: validator
    """
    with open("schema/config_schema.json", "r", encoding="utf-8") as file:
        config_schema = json.load(file)

    schema_files = [
        "schema/functional_dependency_column_usage_schema.json",
        "schema/global_constant_list_column_usage_schema.json",
        "schema/data_convolution_column_usage_schema.json",
        "schema/data_convolution_schema.json",
        "schema/constant_list_schema.json",
        "schema/dataset_schema.json",
        "schema/functional_dependency_schema.json",
        "schema/string_column_schema.json",
        "schema/string_column_constant_list_schema.json",
        "schema/datetime_column_schema.json",
        "schema/datetime_column_sequence_schema.json",
        "schema/datetime_column_datetime_set_schema.json",
        "schema/datetime_column_constant_list_schema.json",
        "schema/date_column_schema.json",
        "schema/date_column_sequence_schema.json",
        "schema/date_column_date_set_schema.json",
        "schema/date_column_constant_list_schema.json",
        "schema/number_column_schema.json",
        "schema/number_column_sequence_schema.json",
        "schema/number_column_number_set_schema.json",
        "schema/number_column_constant_list_schema.json",
    ]

    resources_list = []
    for schema_file in schema_files:
        with open(schema_file, "r", encoding="utf-8") as file:
            schema = json.load(file)
        resources_list.append((schema["$id"], DRAFT7.create_resource(schema)))

    registry = Registry().with_resources(resources_list)
    return Draft7Validator(schema=config_schema, registry=registry)


def get_datasets_list(config, global_structs) -> List[Dataset]:
    """
    Preparing list of config dataset objects
    :param config: parsed generation config
    :param global_structs: global structures class (FDs and constant lists)
    :return: list of datasets
    """

    logging_info(f"Datagen info: Datasets list initialization started.")

    datasets_list = []
    for dataset in config.get("datasets"):

        state = {}
        dataset_name = dataset.get("name")
        output_state_file_name = os.path.join(out_dir, f"{dataset_name}__state__")
        if os.path.exists(output_state_file_name):
            with open(output_state_file_name, "r") as state_file:
                state = json.load(state_file)
        else:
            logging_warning(
                f"Datagen warning: State file not found for dataset {dataset_name} generation."
            )

        dataset_obj = Dataset(dataset, global_structs, state)
        datasets_list.append(dataset_obj)

    logging_info(f"Datagen info: Datasets list initialization ended.")

    return datasets_list


def global_config_validations(config):
    """
    Validations of config
    :param config: parsed generation config
    :return:
    """
    dataset_names = [dataset.get("name") for dataset in config.get("datasets")]
    if len(dataset_names) != len(list(dict.fromkeys(dataset_names))):
        logging_error(
            f"{DATAGEN_VALIDATE_ERROR}In generation config duplicate names of datasets found."
        )

    fd_names = [
        functional_dependency.get("name")
        for functional_dependency in config.get("functional_dependencies", [])
    ]
    if len(fd_names) != len(list(dict.fromkeys(fd_names))):
        logging_error(
            f"{DATAGEN_VALIDATE_ERROR}In generation config duplicate names of functional dependencies found."
        )

    cl_names = [
        constant_lists.get("name") for constant_lists in config.get("constant_lists", [])
    ]
    if len(cl_names) != len(list(dict.fromkeys(cl_names))):
        logging_error(
            f"{DATAGEN_VALIDATE_ERROR}In generation config duplicate names of constant lists found."
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=str, default="config.json", help="path to generation config"
    )
    parser.add_argument(
        "--logfile",
        type=str,
        default="./result/datagen.log",
        help="path to logging output",
    )
    parser.add_argument(
        "--append_log", action="store_true", help="overwrite log or not"
    )
    parser.add_argument(
        "--skip_info", action="store_true", help="log INFO messages or not"
    )
    parser.add_argument(
        "--out_dir", type=str, default="./result/", help="path to logging output"
    )
    args = parser.parse_args()

    config = args.config
    logfile = args.logfile
    out_dir = args.out_dir
    append_log = args.append_log
    skip_info = args.skip_info

    logging.basicConfig(
        filename=logfile,
        filemode="a" if append_log else "w",
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO if not skip_info else logging.WARNING,
    )

    if not os.path.exists(out_dir):
        logging_error(f"{DATAGEN_VALIDATE_ERROR}out_dir {out_dir} path not exists.")

    if not os.path.exists(config):
        logging_error(f"{DATAGEN_VALIDATE_ERROR}config {out_dir} path not exists.")

    try:
        with open(config, "r", encoding="utf-8") as file:
            config = json.load(file)
    except Exception as e:
        logging_error(f"{DATAGEN_VALIDATE_ERROR}Config file parsing error:", e)

    validator = prepare_validator()

    try:
        validator.validate(config)
        logging_info("Datagen info: JSON config matches schema.")
    except ValidationError as e:
        logging_error(f"{DATAGEN_VALIDATE_ERROR}JSON config not matches schema.", e)

    global_structs = GlobalStructs(config)
    global_config_validations(config)
    datasets_list = get_datasets_list(config, global_structs)

    for dataset in datasets_list:
        dataset.generate(out_dir)
