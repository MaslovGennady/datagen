"""
Script for testing validity of generated data by data definition in config
"""

import argparse
import json
import pandas as pd
import logging
import os
import warnings

from datagen.dataset import Dataset
from datagen.global_structuries import GlobalStructs
from datagen.utils import logging_error, logging_info
from test_utils import (
    validate_datetime_column,
    validate_string_column,
    validate_number_column,
)
from datagen.const import WriteMethod

warnings.filterwarnings('ignore', message='subset and superset warning')

parser = argparse.ArgumentParser()
parser.add_argument(
    "--datasets_path", type=str, default="./result/", help="path to datasets"
)
parser.add_argument(
    "--config_path", type=str, default="config.json", help="path to generation config"
)
parser.add_argument(
    "--out_file",
    type=str,
    default="./result/datagen_validation.log",
    help="validation output file",
)
parser.add_argument("--append_result", action="store_true", help="overwrite log or not")
args = parser.parse_args()

datasets_path = args.datasets_path
config_path = args.config_path
out_file = args.out_file
append_result = args.append_result

if not os.path.exists(datasets_path):
    logging_error(f"Datasets path {datasets_path} path not exists.")

if not os.path.exists(config_path):
    logging_error(f"Config path {config_path} path not exists.")

logging.basicConfig(
    filename=out_file,
    filemode="a" if append_result else "w",
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

try:
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)
except Exception as e:
    logging_error(f"Error parsing config from {config_path} ", e)

global_structs = GlobalStructs(config)
datasets_list = []
for dataset_obj in config.get("datasets"):
    datasets_list.append(Dataset(dataset_obj, global_structs, {}))

for dataset in datasets_list:

    column_errors_cnt = 0
    dataset_errors_cnt = 0

    logging_info(f"Starting tests for dataset {dataset.name}")

    try:
        output_file_name = os.path.join(datasets_path, dataset.name)
        # need to ckeck if there are more than one
        if dataset.write_method == WriteMethod.NEW:
            match_filenames = []
            for file in os.listdir(datasets_path):
                if dataset.name in file and '__state__' not in file:
                    match_filenames.append(file)
            if len(match_filenames) == 0:
                logging_error(f"No file contains '{dataset.name}' in file name")
            elif len(match_filenames) > 1:
                match_filenames_str = '\n'.join(match_filenames)
                logging_error(f"Two or more files contain '{dataset.name}' in file name: \n{match_filenames_str}")
            else:
                output_file_name = os.path.join(datasets_path, match_filenames[0])

        # in case of number data for StringColumns we use explicit string type
        string_columns = {}
        for i, column in enumerate(dataset.columns):
            if column.__class__.__name__ == "StringColumn":
                string_columns[i] = str

        df = pd.read_csv(
            output_file_name,
            header=None,
            sep=dataset.separator if dataset.separator else ",",
            dtype=string_columns,
        )

    except Exception as e:
        logging_info(f"Error reading dataset from {datasets_path}{dataset.name}.csv", e)
        continue

    if dataset.write_method != WriteMethod.APPEND:
        dataset_row_count = len(df)
        if dataset.row_count != dataset_row_count:
            dataset_errors_cnt += 1
            logging_info(
                f"Error validating dataset {dataset.name}, dataset.row_count {dataset.row_count} "
                f"not equal to row count in generated data {dataset_row_count}"
            )

    df_column_cnt = len(df.columns)
    logging_info(f"{df_column_cnt} columns found in generated dataset {dataset.name}")

    config_column_names = [column.name for column in dataset.columns]
    config_column_cnt = len(config_column_names)
    logging_info(
        f"{config_column_cnt} columns found in config for dataset {dataset.name}"
    )

    if config_column_cnt != df_column_cnt:
        logging_info(
            f"Can't continue validating dataset {dataset.name}, "
            f"config_column_cnt {config_column_cnt} not equal to df_column_cnt {df_column_cnt}"
        )
    else:
        df.columns = config_column_names
        for column in dataset.columns:
            logging_info(f"Starting tests for column {column.name}")
            try:
                if column.__class__.__name__ == "DatetimeColumn":
                    validate_datetime_column(df, column)
                elif column.__class__.__name__ == "NumberColumn":
                    validate_number_column(df, column)
                elif column.__class__.__name__ == "StringColumn":
                    validate_string_column(df, column)
                else:
                    logging_info(
                        f"Unknown column type for column {column.name}. No validations applied."
                    )

            except Exception as e:
                logging_info(f"Error testing column {column.name}.", e)
                column_errors_cnt += 1

        if column_errors_cnt == 0 and dataset_errors_cnt == 0:
            logging_info(f"Validating dataset {dataset.name} ended OK")
        else:
            logging_info(
                f"Validating dataset {dataset.name} ended NOT OK, {column_errors_cnt} column errors, "
                f"{dataset_errors_cnt} dataset errors."
            )
