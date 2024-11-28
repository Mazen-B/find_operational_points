import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_manager.process_data import filter_data
from src.data_manager.load_data import load_parse_data

class TestFilterData(unittest.TestCase):
    def setUp(self):
        self.test_file = os.path.join("test_IO", "dummy_dataset.csv")
        self.test_dir = "test_IO"

    def save_output(self, df, filename):
        output_path = os.path.join(self.test_dir, filename)
        df.to_csv(output_path, index=False)

    def test_row_to_remove(self):
        """
      In this test, we check if a specific row is removed when row_to_remove is specified.
      """
        row_to_remove = "2024-11-15 11:20:43"
        data = load_parse_data(self.test_file)
        filtered_data = filter_data(data, row_to_remove, [], {})
        self.save_output(filtered_data, "test_row_to_remove.csv")
        self.assertNotIn(
            row_to_remove, filtered_data["time"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
        )

    def test_invalid_row_to_remove_format(self):
        """
      In this test, we check if an invalid row_to_remove format raises an error.
      """
        data = load_parse_data(self.test_file)
        row_to_remove = "invalid-date-format"
        with self.assertRaises(Exception):
            filter_data(data, row_to_remove, [], {})

    def test_keep_only_needed_columns(self):
        """
      In this test, we check if only the needed columns are retained.
      """
        needed_columns = ["time", "orcmode"]
        data = load_parse_data(self.test_file)
        filtered_data = filter_data(data, None, needed_columns, {})
        self.save_output(filtered_data, "test_keep_needed_columns.csv")
        self.assertListEqual(list(filtered_data.columns), needed_columns)

    def test_condition_filtering(self):
        """
      In this test, we check if filtering by a valid condition works correctly.
      """
        conditions = {"orcmode": 5}
        data = load_parse_data(self.test_file)
        filtered_data = filter_data(data, None, [], conditions)
        self.save_output(filtered_data, "test_condition_filtering.csv")
        self.assertTrue(all(filtered_data["orcmode"] == 5))

    def test_invalid_condition_column(self):
        """
        Test if an invalid condition column raises an error.
        """
        data = load_parse_data(self.test_file)
        with self.assertRaises(Exception):
            filter_data(data, None, [], {"orcmodee": 5})

if __name__ == "__main__":
    unittest.main()
