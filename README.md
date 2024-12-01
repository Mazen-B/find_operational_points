# Operational Points Finder

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Graphical User Interface (GUI)](#graphical-user-interface-gui)
  - [Key Features](#key-features)
  - [Usage (GUI Mode)](#usage-gui-mode)
---

## Overview

The Operational Points Finder is a tool designed to identify operational points based on specified conditions, and compute relevant mean values. It supports configurable parameters and offers both command-line and graphical user interface (GUI) modes for ease of use.

---

## Features

- **Flexible Configuration**: Define conditions, time windows, and margins via a YAML configuration file.
- **Supports CSV and Excel Files**: Load and process datasets in `.csv`, `.xlsx`, or `.xls` formats.
- **Data Filtering**: Apply complex filtering rules to extract meaningful operational data.
- **Detailed Logging**: Provides extensive logs for debugging and traceability.
- **GUI Mode**: User-friendly interface for non-technical users to interact with the tool.

---

## Project Structure

```
op_points_finder/
├── config.yaml           # Default configuration file
├── src/                  # Source code directory
│   ├── config/           # Configuration loader and validator
│   ├── core/             # Core logic and operational points analysis
│   │   ├── config_editor_gui.py
│   │   ├── operational_points.py
│   ├── data_manager/     # Data loading and preprocessing modules
│   │   ├── load_data.py
│   │   ├── process_data.py
│   ├── utils/            # Utility modules (e.g., logging, file handling)
│   │   ├── file_management.py
│   │   ├── logging_setup.py
│   └── main.py           # Main entry point for the application
├── tests/                # Test scripts for validating functionality
```

## Configuration File

The `config.yaml` file is the central configuration for the project. It defines parameters for filtering, operational point detection, and statistical computations. Below is an explanation of the key sections in the file:

### Example `config.yaml`
```yaml
1. **`time_window`**:
   - Defines the total time window (in min) for operational point detection.
   - The operational point is considered the **center** of this time window.
   - For example:
     - If `time_window` is set to `2`, the tool evaluates **1 min before** and **1 min after** the operational point.

# Specify the row to remove by date and time (optional)
row_to_remove: "1970-01-01 00:00:00"

# Name of the column containing timestamps
time_column: "time"

# List of columns to calculate mean values for
mean_values:
  - "sens1"
  - "sens2"
  - "sens3"

# Conditions for filtering rows (only 'equals' is supported for now)
conditions:
  sens4: 3

# Margins for validation
margins:
  - column: "temp1"
    margin: 2.0
  - column: "press2"
    margin: 0.5
```

## Graphical User Interface (GUI)

The GUI provides an intuitive interface for users to configure, process, and analyze datasets without needing to edit configuration files manually.

### Key Features

#### Input File Selection:
- Supports both CSV and Excel formats.
- Validates file types to ensure compatibility.

#### Configuration Management:
- Allows default and custom configuration setup.
- Supports defining parameters such as:
  - Time window
  - Conditions
  - Margins
- Provides an interactive interface for easy configuration adjustments.

### Usage (GUI Mode)
---
1. Using Command-Line Mode
  - run **`pip install -r requirements.txt`** once to set up all necessary dependencies.
  - run **`python src/gui/select_files_gui.py`** to run the gui
2. Using batch scripts (Windows):
- Run **`setup_python.bat`** once to set up all necessary dependencies.
- From then on, simply run **`run.bat`** wto run the gui.