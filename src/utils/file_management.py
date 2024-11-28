import os
import logging

def create_output_dir(output_dir):
    """
  This function ensures that the output directory exists. If it does not exist, it creates it.
  """
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Created output directory: {output_dir}")

def cleanup_file_content(output_file):
    """
  This function overwrite the log file so that it can be replaced by new content.
  """
    if os.path.exists(output_file):
      with open(output_file, "w") as file:
          file.write("This is the log file that stores all the printed statement from one run.\n") 
