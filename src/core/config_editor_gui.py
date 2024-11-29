import os
import sys
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from tkinter import filedialog, messagebox 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import analyse_operational_points

class ConfigEditorGUI(ttkb.Window):
    def __init__(self):
        """
      This method initializes class and sets up the main application window with a specified theme, title, size, and needed vars, 
      as well as creates the user interface widgets. 
      """
        super().__init__(themename="cosmo")
        self.title("Main Tool Runner")
        self.geometry("600x650")
        
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
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx;*.xls")])
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

        ttkb.Button(self.conditions_frame, text="Add Condition", bootstyle=INFO, command=self.add_condition).pack(pady=5, anchor="w")

    def add_condition_fields(self, condition):
        """
      This method creates and adds input fields for a condition, including entries for key and value
      """
        frame = ttkb.Frame(self.conditions_frame)
        frame.pack(fill="x", pady=2)

        key_entry = ttkb.Entry(frame, width=20)
        key_entry.insert(0, condition["key"])
        key_entry.pack(side="left", padx=5)

        value_entry = ttkb.Entry(frame, textvariable=condition["value"], width=10)
        value_entry.pack(side="left", padx=5)

        # add Remove button
        remove_button = ttkb.Button(frame, text="Remove", bootstyle=DANGER, command=lambda: self.remove_condition(condition, frame))
        remove_button.pack(side="left", padx=5)

        condition["key_entry"] = key_entry
        condition["value_entry"] = value_entry

    def remove_condition(self, condition, frame):
        """
      This method removes a condition from the conditions list and destroys its associated UI frame
      """
        
        self.conditions.remove(condition)
        # Destroy the frame
        frame.destroy()

    def add_condition(self):
        """
      This method adds a new condition to the conditions list and create input fields for it.
      """
        condition = {"key": "", "value": ttkb.IntVar()}
        self.conditions.append(condition)
        self.add_condition_fields(condition)

    def load_custom_config(self):
        """
      This method loads default values into the custom configuration input fields.
      """
        self.time_window.set(2)
        self.row_to_remove.set("1970-01-01 00:00:00")
        self.time_column.set("time")
        self.mean_values.set("TE201, TE202, TE601, TE701, TE702, PE301, PE303, pelgrossep, pelconsumep")

    def run_custom(self):
        """
      This method runs the tool with the configuration modified by the user.
      """
        if not self.input_file.get() or not self.output_dir.get():
            messagebox.showwarning("Warning", "Please select input and output paths!")
            return

        # build custom config
        custom_config = {
            "time_window": self.time_window.get(),
            "row_to_remove": self.row_to_remove.get(),
            "time_column": self.time_column.get(),
            "mean_values": [val.strip() for val in self.mean_values.get().split(",")],
            "conditions": {cond["key_entry"].get(): cond["value"].get() for cond in self.conditions if cond["key_entry"].get()},
        }

        # run the main.py script with the custom configuration
        run_main(custom_config, self.input_file.get(), self.output_dir.get())


def run_main(config_file, input_file, output_dir):
    """
  This function calls the main.py script to generate the operational points analysis 
  """
    try:
        analyse_operational_points(config_file, input_file, output_dir)
        messagebox.showinfo("Success", "Script executed successfully!")
        app.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        
if __name__ == "__main__":
    app = ConfigEditorGUI()
    app.mainloop()
