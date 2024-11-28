import os
import sys
import logging
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logging_setup import log_and_raise_error

def find_operational_points(data, config):
    """
  This function identifies operational points in a preprocessed df based on dynamic config.
  It returns the operational points and their mean values (according to the specificed time window)
  """
    try:
        # extract configuration values
        time_window = pd.Timedelta(minutes=config["time_window"])
        half_window = time_window / 2
        time_col = config.get("time_column")
        margins = config.get("margins", [])
        needed_columns = config.get("needed_columns", [])

        logging.info("-" * 50)
        logging.info("Starting analysis of operational points.")
        logging.info("-" * 50)

        operational_points = []
        additional_info = []

        for idx, row in data.iterrows():
            current_time = row[time_col]
            logging.info(f"Processing row {idx} with current time: {current_time}")

            # define time windows
            start_time = current_time - half_window
            end_time = current_time + half_window

            logging.info(f"Defined time window: {start_time} to {end_time}")

            # filter data within windows
            window = data[(data[time_col] >= start_time) & (data[time_col] <= end_time)]
            if window.empty:
                logging.info(f"No data found in the window for time {current_time}. Skipping.")
                logging.info("-" * 50)
                continue

            middle_values = row
            logging.info(f"Middle values for current time: {middle_values.to_dict()}")

            # check margins
            conditions_met = True
            for rule in margins:
                column = rule["column"]
                margin = rule["margin"]

                if column not in data.columns:
                    log_and_raise_error(f"Column '{column}' defined in margins is not in the data.")

                diff = (window[column] - middle_values[column]).abs().max()
                logging.info(f"Checking margin for column '{column}' with diff: {diff} and margin: {margin}")

                if diff > margin:
                    logging.info(f"Condition failed for column '{column}'. Diff {diff} exceeds margin {margin}.")
                    conditions_met = False
                    break
                else:
                    logging.info(f"Condition passed for column '{column}'. Diff {diff} within margin {margin}.")

            if conditions_met:
                operational_points.append(current_time)
                logging.info(f"Operational point identified at {current_time}.")

                # calculate mean values for the window
                mean_values = {col: window[col].mean() for col in needed_columns if col != time_col}
                mean_values[time_col] = current_time
                additional_info.append(mean_values)

                logging.info(f"Mean values for time {current_time}: {mean_values}")
            else:
                logging.info(f"No operational point identified at {current_time}.")
            
            logging.info("-" * 50)

        logging.info("Finished analysis of operational points.")
        logging.info(f"Total operational points identified: {len(operational_points)}")
        logging.info("-" * 50)

        return (pd.DataFrame({"Operational Points": operational_points}), pd.DataFrame(additional_info))

    except Exception as e:
        log_and_raise_error(f"An error occurred while finding operational points: {e}")
