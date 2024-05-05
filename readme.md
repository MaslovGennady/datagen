# DataGen
DataGen is a utility for generating data based on a given configuration file and additional data structures. \
The main idea here is to generate a dataset consisting of columns. \
"To generate a dataset" means to generate values for all its columns for the number of times specified in the configuration file. \
For all columns, we have one standard generation method, such as sequence or a set of constants, etc. \
In addition to standard methods, we can use a global set of constants (constant_lists) and key-value structures (functional_dependency).

### Structure
```
datagen project root folder
├── datagen                  # source code
├── examples                 # examples of configs and supporting data for generation
│   ├── config.json          # demo config with all generation cases
│   ├── second_config.json   # demo config with the idea of reusing generated data in the next generation
│   ├── readme.md            # how to execute examples generation (and test it if needed) 
│   └── ...                  # additional data
├── result                   # default destination of generated data and generation/testing logs
├── schema                   # JSON schema for validation generation configs
├── html_doc                 # JSON schema in HTML format generated for friendly exploring (https://github.com/coveooss/json-schema-for-humans)
├── test_utils               # source code for testing data
├── requirements.txt         # generation dependencies 
├── requirements.test.txt    # testing dependencies
├── run_generation.py        # generation script
├── run_tests.py             # testing generated data script
└── README.md                # main readme
```
### Installation
1. Reach the new project destination and start the virtual environment.
   1. Windows
      ```
      python -m venv .venv
      .venv\Scripts\activate
      ```
   2. MacOS, Linux
      ```
      python -m venv .venv
      source .venv/bin/activate
      ```
2. Copy the project's sources to the new project destination.
3. Install generation dependencies.
    ```
    pip install -r requirements.txt
    ```
4. Install testing dependencies.
    ```
    pip install -r requirements.test.txt
    ```
### Generation
Just execute in the root folder of the project:
```
python run_generation.py  
```
The script searches for the config.json file in the root folder, writes generation logs (datagen.log), and result data to the result folder by default. \
After generation, check the contents of the result folder to see if the resulting files and generation logs are there. \
You can change this behavior by modifying the default parameters:
```
python run_generation.py --config="config.json" --logfile="./result/datagen.log" --out_dir="./result/"
```
### Testing
Just execute in the root folder of the project:
```
python run_tests.py  
```
The script searches for the config.json file and the result folder in the root folder, tests the correctness of the generated data, and writes the testing log to the result folder (datagen_validate.log).\
You can change this behavior by modifying the default parameters:
```
python run_tests.py --datasets_path="./result/" --config_path="config.json" --out_file="./result/datagen_validation.log"
```
### Config
For an exact understanding of what DataGen expects in the config, please explore the contents of the schema folder. \
The starting point is config_schema.json. 
```
schema folder
├── date_column                                     # schemas for date column
│   ├── date_column_constant_list_schema.json       # scheme for generating date values from a set of constants 
│   ├── date_column_date_set_schema.json            # scheme for generating date values from a granular set
│   ├── date_column_schema.json                     # general schema for date columns
│   └── date_column_sequence_schema.json            # schema for generating date values as sequence members
├── datetime_column                                 # schemas for datetime column
│   ├── datetime_column_constant_list_schema.json   # schema for generating datetime values from a set of constants 
│   ├── datetime_column_datetime_set_schema.json    # schema for generating datetime values from a granular set
│   ├── datetime_column_schema.json                 # general schema for datetime columns
│   └── datetime_column_sequence_schema.json        # schema for generating datetime values as sequence members
├── number_column                                   # schemas for number columns
│   ├── number_column_constant_list_schema.json     # schema for generating number values from a set of constants  
│   ├── number_column_number_set_schema.json        # schema for generating number values from a granular set
│   ├── number_column_schema.json                   # general schema for number columns
│   └── number_column_sequence_schema.json          # schema for generating number values as sequence members
├── string_column                                   # schemas for string columns
│   ├── string_column_constant_list_schema.json     # schema for generating string values from a set of constants
│   └── string_column_schema.json                   # general schema for string columns
├── config_schema.json                              # general config schema  
├── constant_list_schema.json                       # schema for the global set of constants
├── functional_dependency_column_usage_schema.json  # schema for using key-value structures for generating column values
├── global_constant_list_column_usage_schema.json   # schema for using global constant lists structures for generating column values
├── data_convolution_column_usage_schema.json       # schema for using collapsed data structures for generating column values
└── functional_dependency_schema.json               # schema for key-value structures
```
You can view the configuration file documentation in a convenient format after copying the project files locally and opening the file ./html_doc/config_schema.html \
Big thanks to https://github.com/coveooss/json-schema-for-humans.
### TODO
1. Change jsonschema to pydantic for these reasons:
   1. Native Python syntax.
   2. All validation errors are visible after a single validation.
   3. Easy transition from JSON configuration file to YAML. \
   YAML format appears to be clearer and more user-friendly. \
   Also YAML format allows multi-line values, which can be useful for storing jinja templates.
2. Introduce a generation method that requires a data sample with CSV rows and the required number of them in the dataset (data_convolution).
3. Implement a generation method to generate values with nontrivial distributions.