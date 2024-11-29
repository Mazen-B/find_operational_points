import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_manager.process_data import filter_data
from src.data_manager.load_data import load_parse_data

class TestFilterData(unittest.TestCase):
    def setUp(self):
        # define the vars that will be used in the tests
        self.time_col = "time" # column name was lowercased during configuration loading in config_loader.py
        self.test_dir = "test_IO"
        self.conditions = {"col9": 5}
        self.condition_col = "col9"
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.row_to_remove_1 = "2024-11-15 11:20:43"
        self.row_to_remove_2 = "invalid-date-format"
        self.needed_columns = ["col2", "col3", "col9"]
        self.output_file_1 = "test_row_to_remove.csv"
        self.output_file_2 = "test_keep_needed_columns.csv"
        self.output_file_3 = "test_condition_filtering.csv"
        self.test_file = os.path.join(self.test_dir, "dummy_dataset.csv")
        self.data = load_parse_data(self.test_file, self.time_col)

    def save_output(self, df, filename):
        output_path = os.path.join(self.test_dir, filename)
        df.to_csv(output_path, index=False)

    def test_row_to_remove(self):
        """
      In this test, we check if a specific row is removed when row_to_remove is specified.
      """
        filtered_data = filter_data(self.data, [], self.time_col, {}, self.row_to_remove_1)
        self.save_output(filtered_data, self.output_file_1)
        self.assertNotIn(self.row_to_remove_1, filtered_data[self.time_col].dt.strftime(self.date_format).tolist())

    def test_invalid_row_to_remove_format(self):
        """
      In this test, we check if an invalid row_to_remove format raises an error.
      """
        with self.assertRaises(Exception):
            filter_data(self.data, [], self.time_col, {}, self.row_to_remove_2)

    def test_keep_only_needed_columns(self):
        """
      In this test, we check if only the needed columns are retained.
      """
        filtered_data = filter_data(self.data, self.needed_columns, self.time_col, {}, None)
        self.save_output(filtered_data, self.output_file_2)
        remaining_columns = [self.time_col] + self.needed_columns
        self.assertListEqual(list(filtered_data.columns), remaining_columns)

    def test_condition_filtering(self):
        """
      In this test, we check if filtering by a valid condition works correctly.
      """
        filtered_data = filter_data(self.data, self.needed_columns, self.time_col, self.conditions, None)
        self.save_output(filtered_data, self.output_file_3)
        self.assertTrue(all(filtered_data[self.condition_col] == 5))

    def test_invalid_condition_column(self):
        """
      In this test, we check if an invalid condition column raises an error.
      """
        with self.assertRaises(Exception):
            filter_data(self.data, None, [], {"orcmodee": 5})

if __name__ == "__main__":
    unittest.main()
