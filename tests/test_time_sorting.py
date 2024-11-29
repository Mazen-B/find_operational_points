import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_manager.load_data import load_parse_data

class TestLoadParseData(unittest.TestCase):
    def setUp(self):
        self.time_col = "time"
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.test_file = os.path.join("test_IO", "dummy_dataset.csv")

    def test_sorting_in_csv(self):
        """
      In this test, we test that the load_parse_data is able to load, normalize the columns, and sort the time column 
      from the dummy dataset. Successfully sorting the data by the "time" column indicates that the preceding steps
      (loading and normalizing columns) were executed successfully.
      """
        # call the load_parse_data function
        sorted_data = load_parse_data(self.test_file, self.time_col)

        # extract the sorted "time" column as a list of strings
        sorted_times = sorted_data[self.time_col].dt.strftime(self.date_format).tolist()

        # expected sorted values based on the dummy dataset
        expected_sorted_times = [
            "2024-11-12 14:20:03",
            "2024-11-12 15:42:53",
            "2024-11-12 17:25:23",
            "2024-11-13 09:30:53",
            "2024-11-13 10:25:13",
            "2024-11-13 11:38:33",
            "2024-11-13 13:45:43",
            "2024-11-14 08:55:23",
            "2024-11-14 12:40:23",
            "2024-11-14 16:00:33",
            "2024-11-15 09:14:43",
            "2024-11-15 11:20:43",
            "2024-11-15 13:10:03"
        ]

        # assert that the sorted times match the expected values
        self.assertListEqual(sorted_times, expected_sorted_times)

if __name__ == "__main__":
    unittest.main()