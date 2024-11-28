import os
import sys
import logging
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logging_setup import log_and_raise_error

def find_operational_points(data, time_col, mean_values, config):
    """
  This function identifies operational points in a preprocessed df based on a dynamic config.
  It returns the operational points and their mean values (according to the specified time window).
  """
    try:
        # extract configuration values
        time_window = pd.Timedelta(minutes=config["time_window"])
        half_window = time_window / 2
        margins = config.get("margins", [])

        logging.info("-" * 50)
        logging.info("Starting analysis of operational points.")
        logging.info("-" * 50)

        operational_points = []
        additional_info = []

        # calculate the proper start index
        start_time = data[time_col].iloc[0] + half_window
        start_row = data[data[time_col] == start_time]
        if start_row.empty:
            start_row = data[data[time_col] > start_time].iloc[0:1]
        idx = start_row.index[0]

        while idx < len(data):
            row = data.iloc[idx]
            current_time = row[time_col]
            logging.info(f"Processing row {idx + 2} with current time: {current_time}")

            # define time window
            start_time = current_time - half_window
            end_time = current_time + half_window
            logging.info(f"Defined time window: {start_time} to {end_time}")

            # split the window into before and after
            before_window = data[(data[time_col] >= start_time) & (data[time_col] < current_time)]
            after_window = data[(data[time_col] > current_time) & (data[time_col] <= end_time)]

            if before_window.empty or after_window.empty:
                logging.info(f"No sufficient data in before or after window for time {current_time}. Skipping.")
                logging.info("-" * 50)
                idx += 1
                continue

            middle_values = row
            logging.info(f"Middle values for current time: {middle_values.to_dict()}")

            # check margins for before and after windows
            conditions_met = True
            for rule in margins:
                column = rule["column"]
                margin = rule["margin"]

                if column not in data.columns:
                    log_and_raise_error(f"Column '{column}' defined in margins is not in the data.")

                # check before window
                before_within_margin = all(abs(before_window[column] - middle_values[column]) <= margin)
                if not before_within_margin:
                    logging.info(f"Condition failed for column '{column}' in before window.")
                    conditions_met = False
                    break

                # check after window
                after_within_margin = all(abs(after_window[column] - middle_values[column]) <= margin)
                if not after_within_margin:
                    logging.info(f"Condition failed for column '{column}' in after window.")
                    conditions_met = False
                    break

                logging.info(f"Condition passed for column '{column}' in both before and after windows.")

            if conditions_met:
                operational_points.append(current_time)
                logging.info(f"Operational point identified at {current_time}.")

                # calculate mean values for the window
                mean_values_dict = {col: data[(data[time_col] >= start_time) & (data[time_col] <= end_time)][col].mean() for col in mean_values if col != time_col}
                mean_values_dict[time_col] = current_time
                additional_info.append(mean_values_dict)

                logging.info(f"Mean values for time {current_time}: {mean_values_dict}")

                # skip half a window to avoid overlapping operational points
                next_time = current_time + half_window

                # Check if 'next_time' is beyond the last timestamp
                if next_time > data[time_col].iloc[-1]:
                    break

                # Find the next index
                remaining_data = data[data[time_col] >= next_time]
                if remaining_data.empty:
                    break
                idx = remaining_data.index[0]
            else:
                logging.info(f"No operational point identified at {current_time}.")
                idx += 1

            logging.info("-" * 50)

        logging.info("Finished analysis of operational points.")
        logging.info(f"Total operational points identified: {len(operational_points)}")
        logging.info("-" * 50)

        return pd.DataFrame({"Operational Points": operational_points}), pd.DataFrame(additional_info)

    except Exception as e:
        log_and_raise_error(f"An error occurred while finding operational points: {e}")

