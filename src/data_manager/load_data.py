import os
import sys
import logging
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logging_setup import log_and_raise_error

def load_parse_data(input_file, time_col):
    """
  This function loads data from a CSV or Excel file, parses the "time" column as datetime, sort by the "time" column.
  """
    try:
        if input_file.endswith(".csv"):
            data = pd.read_csv(input_file)
            logging.info("CSV file was loaded successfully.")
        elif input_file.endswith(".xlsx"):
            data = pd.read_excel(input_file)
            logging.info("Excel file was loaded successfully.")
        else:
            log_and_raise_error("Unsupported file format. Please select a CSV or Excel file.")

        # normalize column names to lowercase
        data.columns = data.columns.str.lower()

        # parse the "time" column as datetime
        if time_col not in data.columns:
            log_and_raise_error("'time' column is missing in the input file.")
        data[time_col] = pd.to_datetime(data[time_col])

        # sort the data by the "time" column
        data = data.sort_values(by=time_col).reset_index(drop=True)

        if data is None or data.empty:
            log_and_raise_error("Empty data after loading from the input file.")
        if not isinstance(data, pd.DataFrame):
            log_and_raise_error("Loaded data is not a pandas DataFrame.")
        return data

    except FileNotFoundError:
        log_and_raise_error("The specified file was not found. Please check the file path.")
    except pd.errors.EmptyDataError:
        log_and_raise_error("The file is empty. No data to process.")
    except ValueError as ve:
        log_and_raise_error(f"Value error: {ve}")
    return None