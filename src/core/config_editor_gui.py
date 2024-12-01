import os
import sys
import yaml
import logging
import tempfile
import traceback
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import analyse_operational_points
from config.validate_config import validate_config

class ConfigEditorGUI(ttkb.Window):
    def __init__(self):
        """
      This method initializes class and sets up the main application window with a specified theme, title, size, and needed vars, 
      as well as creates the user interface widgets. 
      """
        super().__init__(themename="cosmo")
        self.title("Main Tool Runner")
        self.geometry("800x850")
        
        self.input_file = ttkb.StringVar()
        self.output_dir = ttkb.StringVar()
        
        self.default_config_path = os.path.join("config.yaml")
        self.custom_config_data = None

        self.create_widgets()

    def create_widgets(self):
        """
      This is the main method that creates the widgets
      """
        # configure column weights
        self.columnconfigure(0, weight=1)

        # frame for Input File
        input_frame = ttkb.Frame(self)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ttkb.Label(input_frame, text="Input File", width=15, anchor="w").pack(side="left", padx=5)
        ttkb.Entry(input_frame, textvariable=self.input_file, width=50).pack(side="left", padx=5)
        ttkb.Button(input_frame, text="Browse", bootstyle=INFO, command=self.select_input_file).pack(side="left", padx=5)

        # frame for Output Directory
        output_frame = ttkb.Frame(self)
        output_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        ttkb.Label(output_frame, text="Output Directory", width=15, anchor="w").pack(side="left", padx=5)
        ttkb.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side="left", padx=5)
        ttkb.Button(output_frame, text="Browse", bootstyle=INFO, command=self.select_output_dir).pack(side="left", padx=5)

        # "Run Default Config" Button
        ttkb.Button(self, text="Run Default Config", bootstyle=PRIMARY, command=self.run_default).grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # custom Configuration Option
        self.custom_input_var = ttkb.BooleanVar()
        ttkb.Checkbutton(
            self, text="Modify Default Config", variable=self.custom_input_var,
            bootstyle="primary-round-toggle", command=self.toggle_custom_input
        ).grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # frame for custom configuration
        self.custom_frame = ttkb.Frame(self)
        self.custom_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        self.custom_frame.grid_remove()  # hide initially

        self.config_fields = {}
        self.create_custom_config_fields()

        self.run_custom_button = ttkb.Button(self.custom_frame, text="Run with Custom Config", bootstyle=PRIMARY, command=self.run_custom)
        self.run_custom_button.pack(pady=10, anchor="w")

    def select_input_file(self):
        """
      This method opens a file dialog to select an input file (CSV or Excel) and store the file path.
      """
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV and Excel Files", ("*.csv", "*.xlsx", "*.xls"))])
        if file_path:
            self.input_file.set(file_path)

    def select_output_dir(self):
        """
      This method opens a dir dialog to select an output dir and store the file path.
      """
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def run_default(self):
        """
      This method run the tool with the default configuration and selected input/output paths
      """
        if not self.input_file.get() or not self.output_dir.get():
            messagebox.showwarning("Warning", "Please select input and output paths!")
            return
        run_main(self.default_config_path, self.input_file.get(), self.output_dir.get())

    def toggle_custom_input(self):
        """
      This method shows or hides the custom configuration frame based on user selection.
      """
        if self.custom_input_var.get():
            self.custom_frame.grid()
            self.load_custom_config()
        else:
            self.custom_frame.grid_remove()

    def create_custom_config_fields(self):
        """
      This method creates and configures input fields for custom configuration settings (if the user wants to modify the default config).
      """
        # Time Window
        time_window_frame = ttkb.Frame(self.custom_frame)
        time_window_frame.pack(fill="x", pady=2)
        ttkb.Label(time_window_frame, text="Time Window").pack(side="left")
        help_button = ttkb.Label(time_window_frame, text="?", foreground="blue")
        help_button.pack(side="left", padx=5)
        ToolTip(help_button, text="Enter the time window in min (the captured op point will be in the middle).")
        self.time_window = ttkb.IntVar(value=2)
        time_window_entry = ttkb.Entry(self.custom_frame, textvariable=self.time_window, width=30)
        time_window_entry.pack(fill="x")

        # Row to Remove
        row_to_remove_frame = ttkb.Frame(self.custom_frame)
        row_to_remove_frame.pack(fill="x", pady=2)
        ttkb.Label(row_to_remove_frame, text="Row to Remove").pack(side="left")
        help_button = ttkb.Label(row_to_remove_frame, text="?", foreground="blue")
        help_button.pack(side="left", padx=5)
        ToolTip(help_button, text="Specify the row to remove by date and time (can also be left empty).")
        self.row_to_remove = ttkb.StringVar(value="1970-01-01 00:00:00")
        row_to_remove_entry = ttkb.Entry(self.custom_frame, textvariable=self.row_to_remove, width=30)
        row_to_remove_entry.pack(fill="x")

        # Time Column
        time_column_frame = ttkb.Frame(self.custom_frame)
        time_column_frame.pack(fill="x", pady=2)
        ttkb.Label(time_column_frame, text="Time Column").pack(side="left")
        help_button = ttkb.Label(time_column_frame, text="?", foreground="blue")
        help_button.pack(side="left", padx=5)
        ToolTip(help_button, text="Enter the name of the time column.")
        self.time_column = ttkb.StringVar(value="Time")
        time_column_entry = ttkb.Entry(self.custom_frame, textvariable=self.time_column, width=30)
        time_column_entry.pack(fill="x")

        # Mean Values
        mean_values_frame = ttkb.Frame(self.custom_frame)
        mean_values_frame.pack(fill="x", pady=2)
        ttkb.Label(mean_values_frame, text="Mean Values").pack(side="left")
        help_button = ttkb.Label(mean_values_frame, text="?", foreground="blue")
        help_button.pack(side="left", padx=5)
        ToolTip(help_button, text="Enter mean values separated by commas.")
        self.mean_values = ttkb.StringVar(value="TE201, TE202, TE601, TE701, TE702, PE301, PE303, pelgrossep, pelconsumep")
        mean_values_entry = ttkb.Entry(self.custom_frame, textvariable=self.mean_values, width=30)
        mean_values_entry.pack(fill="x")

        # Conditions
        conditions_frame = ttkb.Frame(self.custom_frame)
        conditions_frame.pack(fill="x", pady=2)
        ttkb.Label(conditions_frame, text="Conditions").pack(side="left")
        help_button = ttkb.Label(conditions_frame, text="?", foreground="blue")
        help_button.pack(side="left", padx=5)
        ToolTip(help_button, text="Add conditions with key-value pairs for filtering (for now only 'equals' is implemented).")

        self.conditions_frame = ttkb.Frame(self.custom_frame)
        self.conditions_frame.pack(fill="x", pady=5)

        # add default condition
        self.conditions = [{"key": "orcmode", "value": ttkb.IntVar(value=3)}]
        self.add_condition_fields(self.conditions[0])

        # Margins
        margins_frame = ttkb.Frame(self.custom_frame)
        margins_frame.pack(fill="x", pady=2)
        ttkb.Label(margins_frame, text="Margins").pack(side="left")
        help_button = ttkb.Label(margins_frame, text="?", foreground="blue")
        help_button.pack(side="left", padx=5)
        ToolTip(help_button, text="Specify columns and margins as key-value pairs.")

        self.margins_frame = ttkb.Frame(self.custom_frame)
        self.margins_frame.pack(fill="x", pady=5)

        # add default margin
        self.margins = [{"column": ttkb.StringVar(value="te201"), "margin": ttkb.DoubleVar(value=2.0)}]
        self.add_margin_fields(self.margins[0])

    #####################################
    # helper functions for adding entries
    #####################################
    def add_entry_fields(self, parent_frame, item, add_after_func, remove_func, field_defs):
        """
      This method is a general method to create and add input fields for an item, including entries for key and value,
      and adds "+" and "x" buttons for adding/removing items.
      """
        frame = ttkb.Frame(parent_frame)
        item["frame"] = frame

        frame.pack(fill="x", pady=2)

        # create fields based on field_defs
        for field_def in field_defs:
            if "label" in field_def:
                ttkb.Label(frame, text=field_def["label"]).pack(side="left", padx=5)
            entry = ttkb.Entry(frame, textvariable=field_def["variable"], width=field_def.get("width", 20))
            entry.pack(side="left", padx=5)
            if "entry_name" in field_def:
                item[field_def["entry_name"]] = entry

        # "+" button to add a new item after this one
        add_button = ttkb.Button(
            frame,
            text="➕",
            bootstyle="success-outline",
            command=lambda: add_after_func(item),
            width=2,
            padding=0
        )
        add_button.pack(side="right", padx=3)

        # "x" button to remove this item
        remove_button = ttkb.Button(
            frame,
            text="✖",
            bootstyle="danger-outline",
            command=lambda: remove_func(item),
            width=2,
            padding=0
        )
        remove_button.pack(side="right", padx=3)

    ###############################################
    # helper functions for the "Conditions" Section
    ###############################################
    def add_condition_fields(self, condition):
        condition["key_var"] = ttkb.StringVar(value=condition.get("key", ""))
        condition["value_var"] = condition.get("value", ttkb.IntVar())

        field_defs = [
            {"label": "Key:", "variable": condition["key_var"], "width": 20, "entry_name": "key_entry"},
            {"label": "Value:", "variable": condition["value_var"], "width": 10, "entry_name": "value_entry"}
        ]

        self.add_entry_fields(
            parent_frame=self.conditions_frame,
            item=condition,
            add_after_func=self.add_condition_after,
            remove_func=self.remove_condition,
            field_defs=field_defs
        )

    def remove_condition(self, condition):
        self.conditions.remove(condition)
        condition["frame"].destroy()

    def add_condition_after(self, condition):
        index = self.conditions.index(condition)
        new_condition = {"key": "", "value": ttkb.IntVar()}
        self.conditions.insert(index + 1, new_condition)
        self.add_condition_fields(new_condition)
        new_condition["frame"].pack(after=condition["frame"])

    ############################################
    # helper functions for the "Margins" Section
    ############################################
    def add_margin_fields(self, margin):
        field_defs = [
            {"label": "Column:", "variable": margin["column"], "width": 20, "entry_name": "column_entry"},
            {"label": "Margin:", "variable": margin["margin"], "width": 10, "entry_name": "margin_entry"}
        ]
        self.add_entry_fields(
            parent_frame=self.margins_frame,
            item=margin,
            add_after_func=self.add_margin_after,
            remove_func=self.remove_margin,
            field_defs=field_defs
        )

    def add_margin_after(self, margin):
        index = self.margins.index(margin)
        new_margin = {"column": ttkb.StringVar(), "margin": ttkb.DoubleVar()}
        self.margins.insert(index + 1, new_margin)
        self.add_margin_fields(new_margin)
        new_margin["frame"].pack(after=margin["frame"])

    def remove_margin(self, margin):
        self.margins.remove(margin)
        margin["frame"].destroy()

    def load_custom_config(self):
        """
      This method loads default values into the custom configuration input fields.
      """
        self.time_window.set(2)
        self.row_to_remove.set("1970-01-01 00:00:00")
        self.time_column.set("time")
        self.mean_values.set("TE201, TE202, TE601, TE701, TE702, PE301, PE303, pelgrossep, pelconsumep")

        # clear existing margins and conditions
        for condition in self.conditions[:]:
            self.remove_condition(condition)
        for margin in self.margins[:]:
            self.remove_margin(margin)

        # re-add default condition
        self.conditions = [{"key": "orcmode", "value": ttkb.IntVar(value=3)}]
        self.add_condition_fields(self.conditions[0])

        # re-add default margins
        self.margins = [
            {"column": ttkb.StringVar(value="te201"), "margin": ttkb.DoubleVar(value=2.0)},
            {"column": ttkb.StringVar(value="pe301"), "margin": ttkb.DoubleVar(value=0.5)},
            {"column": ttkb.StringVar(value="pelgrossep"), "margin": ttkb.DoubleVar(value=5.0)}
        ]

        for margin in self.margins:
            self.add_margin_fields(margin)

    def run_custom(self):
        """
      This method runs the tool with the user-modified configuration.
      """
        try:
            # build the custom configuration
            custom_config = {
                "time_window": self.time_window.get(),
                "row_to_remove": self.row_to_remove.get(),
                "time_column": self.time_column.get(),
                "mean_values": [val.strip() for val in self.mean_values.get().split(",")],
                "conditions": {cond["key_entry"].get(): cond["value"].get() for cond in self.conditions if cond["key_entry"].get()},
                "margins": [{"column": margin["column"].get(), "margin": margin["margin"].get()} for margin in self.margins]
            }

            # validate the configuration
            validated_config = validate_config(custom_config)

            # write the custom configuration and execute
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as temp_config_file:
                yaml.dump(validated_config, temp_config_file)
                temp_config_file_path = temp_config_file.name

            # run the main process with the temporary config file path
            run_main(temp_config_file_path, self.input_file.get(), self.output_dir.get())

        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            logging.error("Unexpected error: %s", e, exc_info=True)
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def run_main(config_file, input_file, output_dir):
    """
  This function calls the main.py script to generate the operational points analysis 
  """
    try:
        analyse_operational_points(config_file, input_file, output_dir)
        messagebox.showinfo("Success", "Script executed successfully!")
        app.destroy()
    except ValueError as ve:
        messagebox.showerror("Validation Error", str(ve))
    except Exception as e:
        logging.error("An unexpected error occurred: %s", traceback.format_exc())
        error_message = f"An unexpected error occurred:\n{str(e)}"
        messagebox.showerror("Error", error_message)
        
if __name__ == "__main__":
    app = ConfigEditorGUI()
    app.mainloop()
