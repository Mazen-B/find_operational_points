import os
import logging
from data_manager.process_data import filter_data
from data_manager.load_data import load_parse_data
from utils.logging_setup import initialize_logging
from utils.logging_setup import log_and_raise_error
from config.config_loader import load_validate_config
from core.operational_points import find_operational_points

def analyse_operational_points(input_file, output_dir):
    """
  This function serves as the orchestrator for loading, processing, extracting the operational points
  and their mean values, and saving outputs.
  """
    try:
        # specify the ouptput files
        filtered_data_file = os.path.join(output_dir, "filtered_data.csv")
        op_points_file = os.path.join(output_dir, "operational_points.csv")
        additional_info_file = os.path.join(output_dir, "op_mean_values.csv")

        # Step 1: get the needed input vars from the config file
        config_file = "config.yaml"
        config = load_validate_config(config_file)

        # Step 2: load and parse the data
        data = load_parse_data(input_file, config["time_column"])

        # Step 3: clean and filter the data
        filtered_data = filter_data(data, config["row_to_remove"], config["needed_columns"], config["conditions"], config["time_column"])
        print("what is filtered_data: ", filtered_data)
        # save the filtered data to a CSV
        filtered_data.to_csv(filtered_data_file, index=False)
        logging.info("Filtered data saved to %s", filtered_data_file)

        # Step 4: get the operational points with their mean values
        op_points_df, additional_info_df = find_operational_points(filtered_data, config)

        # save operational points and mean values to a CSV
        op_points_df.to_csv(op_points_file, index=False)
        additional_info_df.to_csv(additional_info_file, index=False)
        logging.info("Operational points saved to %s", op_points_file)
        logging.info("Additional info saved to %s", additional_info_file)

        return filtered_data, op_points_df, additional_info_df

    except Exception as e:
        log_and_raise_error(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    file_path = os.path.join("inputs", "combined_file.csv")
    output_dir = os.path.join("outputs")

    initialize_logging(output_dir)
    analyse_operational_points(file_path, output_dir)
