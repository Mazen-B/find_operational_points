import os
import sys
import yaml
import logging
from config.validate_config import validate_config

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logging_setup import log_and_raise_error

def load_validate_config(config_file):
    """
  This function loads and validates the configuration from the YAML file.
  """
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        logging.info("Configuration file %s loaded successfully.", config_file)

        validate_config(config)
        logging.info("Configuration validated successfully.")
        return config

    except FileNotFoundError:
        log_and_raise_error(f"Configuration file {config_file} not found.")
    except yaml.YAMLError as e:
        log_and_raise_error(f"Error parsing YAML config file: {e}")
