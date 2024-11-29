import os
import logging
from utils.file_management import create_output_dir, cleanup_file_content

def initialize_logging(output_dir):
    """
  This function initializes logging with the specified level, console and file logging, and log rotation.
  """
    # create the output directory, if it does not exist
    create_output_dir(output_dir)
    log_file_name = "logging_output.txt"
    log_file = os.path.join(output_dir, log_file_name)
    cleanup_file_content(log_file)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )
    logging.info("Logging initialized. Logs are being saved to %s", log_file)

def log_and_raise_error(message):
    """
  This function logs an error message and raises a ValueError with the same message.
  """
    logging.error(message)
    raise ValueError(message)
