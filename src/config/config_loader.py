import os
import sys
import yaml
import logging
from config.validate_config import validate_config

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logging_setup import log_and_raise_error

def load_validate_config(config_file):
    """
  This function loads and validates the configuration from the YAML file, and returns the time_column 
  and needed_columns in lowercase.
  """
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        logging.info("Configuration file %s loaded successfully.", config_file)

        validate_config(config)
        logging.info("Configuration validated successfully.")

        # extract and convert to lowercase
        time_column = config["time_column"].lower()
        needed_columns, mean_values = get_needed_columns(config)

        return time_column, needed_columns, mean_values, config

    except FileNotFoundError:
        log_and_raise_error(f"Configuration file {config_file} not found.")
    except yaml.YAMLError as e:
        log_and_raise_error(f"Error parsing YAML config file: {e}")


def get_needed_columns(config):
    """
  This funcion extracts and processes columns from mean_values, conditions, and margins in the config.
  It also converts all column names to lowercase, removes duplicates, and returns the list.
  """
    # extract mean_values columns, condition and mean values columns
    mean_values = config.get("mean_values", [])
    conditions = config.get("conditions", {})
    condition_columns = list(conditions.keys())
    margins = config.get("margins", [])
    margin_columns = [margin["column"] for margin in margins]

    # combine all columns
    all_columns = mean_values + condition_columns + margin_columns

    # convert to lowercase and remove duplicates
    needed_columns = list(set([col.lower() for col in all_columns]))
    mean_values = [col.lower() for col in config["mean_values"]]

    return needed_columns, mean_values
