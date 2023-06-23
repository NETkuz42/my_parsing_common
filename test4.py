import my_help_func

path_to_dir_test_result = r"data\country_tests"

result = my_help_func.sorted_files_by_date(path_to_dir_test_result)[-1]

print(result)