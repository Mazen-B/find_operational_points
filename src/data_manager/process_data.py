import os
import sys
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logging_setup import log_and_raise_error

def filter_data(data, needed_columns, time_col, conditions, row_to_remove):
    """
  This function filters data in a CSV or Excel file based on specified conditions.
  """
    try:
        # Step 1: remove rows with the specific value in the "time" column
        if row_to_remove:
            original_row_count = len(data)
            
            # ensure row_to_remove has a valid datetime format
            try:
                datetime.strptime(row_to_remove, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                log_and_raise_error(f"Invalid datetime format for 'row_to_remove': {row_to_remove}. Expected format: 'YYYY-MM-DD HH:MM:SS'")
            
            data = data[data[time_col] != row_to_remove]
            removed_row_count = original_row_count - len(data)
            
            logging.info(f"Filtering: Removed {removed_row_count} rows with time value '{row_to_remove}'.")
        
        # Step 2: keep only the needed columns
        all_columns = [time_col] + needed_columns
        missing_columns = [col for col in all_columns if col not in data.columns]
        if missing_columns:
            log_and_raise_error(f"The following columns are missing: {', '.join(missing_columns)}")

        data = data[all_columns]
        logging.info(f"Filtering: Kept only the time column '{time_col}' and the specified columns: {', '.join(needed_columns)}.")
        
        # Step 3: apply conditions (only "equals" conditions supported)
        # convert the column specified in the condition to lowercase then check if it exists
        conditions = {col.lower(): value for col, value in conditions.items()}
        for column, value in conditions.items():
            if column not in data.columns:
                log_and_raise_error(f"Column '{column}' not found in the data.")
            
            # ensure condition values are of the correct type (column names and integer values)
            if not isinstance(value, int):
                log_and_raise_error(f"Condition for column '{column}' has an invalid value type: Expected an int, got {type(value).__name__}")

            original_row_count = len(data)
            data = data[data[column] == value]
            filtered_row_count = original_row_count - len(data)
            
            logging.info(f"Filtering: Applied 'equals' condition on column '{column}' with value {value}. Filtered {filtered_row_count} rows.")
        
        if data.empty:
            log_and_raise_error("Filtered data is empty. No CSV file will be saved.")

        # reset index after filtering
        data = data.reset_index(drop=True)
        return data

    except ValueError as ve:
        log_and_raise_error(f"Value error: {ve}")
    except Exception as e:
        log_and_raise_error(f"An unexpected error occurred: {e}")
