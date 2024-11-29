import os
import sys
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_manager.process_data import filter_data
from src.data_manager.load_data import load_parse_data
from src.core.operational_points import find_operational_points 

class TestFindOperationalPoints(unittest.TestCase):
    def setUp(self):
        self.time_col = "time"
        self.mean_values = ["col1", "col2", "col3"]
        self.needed_columns = ["col1", "col2", "col3", "col4", "col5", "col6", "col7"]
        self.test_file = os.path.join("test_IO", "op_dataset.csv")
        self.data = load_parse_data(self.test_file, self.time_col)
        self.filtered_data = filter_data(self.data, self.needed_columns, self.time_col, {}, None)
        self.config = {
            "time_window": 1,  # 1 min
            "margins": [
                {"column": "col1", "margin": 1},
                {"column": "col3", "margin": 0.5},
            ]
        }
    def test_valid_operational_points(self):
        """
      In this test, we check if the correct operational points are being captured, and if their calculated mean values are correct.
      """
        op_points, additional_info = find_operational_points(self.filtered_data, self.time_col, self.mean_values, self.config)

        expected_op_points = pd.DataFrame({
            "Operational Points": [
                pd.Timestamp("2024-11-12 10:00:00"),
                pd.Timestamp("2024-11-13 10:00:00"),
                pd.Timestamp("2024-11-14 10:00:00")
            ]
        })

        expected_additional_info = pd.DataFrame({
            "time": [
                pd.Timestamp("2024-11-12 10:00:00"),
                pd.Timestamp("2024-11-13 10:00:00"),
                pd.Timestamp("2024-11-14 10:00:00")
            ],
            "col1": [100.0, 110.0, 105.0],
            "col2": [99.5, 99.5, 99.5],
            "col3": [50.0, 60.0, 55.0]
        })

        assert_frame_equal(op_points, expected_op_points)
        assert_frame_equal(additional_info, expected_additional_info, atol=1e-2)

    def test_no_false_operational_points(self):
        """
      In this test, we ensure that the function does not capture operational points when the conditions are not met.
      We modify the data slightly so that an operational point should not be captured.
      """
        modified_data = self.filtered_data.copy()

        # increase "col1" at "2024-11-13 10:00:00" to exceed the margin
        modified_data.loc[
            modified_data[self.time_col] == pd.Timestamp("2024-11-13 10:00:00"), "col1"
        ] = 112.0  # original value was 110.0

        op_points, additional_info = find_operational_points(modified_data, self.time_col, self.mean_values, self.config)

        expected_op_points = pd.DataFrame({
            "Operational Points": [
                pd.Timestamp("2024-11-12 10:00:00"),
                pd.Timestamp("2024-11-14 10:00:00")
            ]
        })

        expected_additional_info = pd.DataFrame({
            "time": [
                pd.Timestamp("2024-11-12 10:00:00"),
                pd.Timestamp("2024-11-14 10:00:00")
            ],
            "col1": [100.0, 105.0],
            "col2": [99.5, 99.5],
            "col3": [50.0, 55.0]
        })

        assert_frame_equal(op_points, expected_op_points)
        assert_frame_equal(additional_info, expected_additional_info, atol=1e-2)

        # add the check that "2024-11-13 10:00:00" is not in op_points
        self.assertNotIn(pd.Timestamp("2024-11-13 10:00:00"), op_points["Operational Points"].values)
    
if __name__ == "__main__":
    unittest.main()
