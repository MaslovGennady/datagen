Instructions for executing examples generation:

1. Explore config.json and second_config.json contents 
2. Execute from the root of the project 
    ```
    python run_generation.py --config="./examples/config.json"
    ```
3. If you want to test your data 
    ```
    python run_tests.py --config_path="./examples/config.json"
    ```
4. Сheck the result in folder named "result"
5. Execute from the root of the project 
    ```
    python run_generation.py --config="./examples/second_config.json"
    ```
6. If you want to test your data 
    ```
    python run_tests.py --config_path="./examples/second_config.json"
    ```
7. Сheck the result in folder named "result"

What we end up with: 
1. datagen.log - default name of generation log file
2. datagen_validation.log - default name of data testing log file
3. first_test_dataset - dataset with listing of all possible cases of column generation
4. second_test_dataset - dataset that will serve as a functional dependency for other dataset generation
5. dc_test_dataset - dataset generated using collapsed data template (data_convolution)
6. dataset_generate_dc_template - dataset that will serve as a data convolution for other dataset generation 
7. third_test_dataset - dataset generated using functional dependency from second_test_dataset
8. dataset_from_generated_dc - dataset generated using data convolution from dataset_generate_dc_template
