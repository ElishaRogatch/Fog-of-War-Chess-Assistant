from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import chess
import tkinter as tk
import configparser
import copy
import os
from dataclasses import dataclass, field
from typing import Any, Dict
from gui_io import YesNoIO
from utils import to_color, str_to_bool
from tkinter import filedialog


class GameSettings():
    """Used as a link to get settings in the main program."""
    # Should be updated anytime one of the names used as keys in settings_structure is updated.
    def __init__(self):
        settings_dict = SettingsManager.load_settings()
        # UserSettings
        self.assisted_player: chess.Color = to_color(settings_dict["UserSettings"]["assisted_player"])
        self.search_depth: int = settings_dict["UserSettings"]["search_depth"]
        self.suggested_moves_count: int = settings_dict["UserSettings"]["suggested_moves_count"]
        # LogSettings
        self.logs_per_folder: int = settings_dict["LogSettings"]["logs_per_folder"]
        self.use_custom_log_path: bool = settings_dict["LogSettings"]["use_custom_path"]
        self.custom_log_path: str = settings_dict["LogSettings"]["custom_path"]

class SettingsManager(tk.Toplevel):
    """Display the settings menu allowing users to change settings."""
    @dataclass
    class Setting:
        default_value: Any
        display_name: str
        widget_type: str
        height: int # approximate height in lines
        options: Dict[str, Any] = field(default_factory=dict)
        
    @dataclass
    class Section:
        display_name:str
        public_setting:bool
        settings: Dict[str, SettingsManager.Setting] = field(default_factory=dict)
    
    settings_structure = {
        "UserSettings" : Section(
            "User Settings", 
            True,
            settings = {
                "assisted_player" : Setting(
                    "white", 
                    "Assisted Player", 
                    "dropdown",
                    2, 
                    {"dropdown_options" : ["white", "black"]}
                ),
                "search_depth" : Setting(
                    10,
                    "Search Depth\nMatch your time per turn to the table below\n1-5\t6-10\t11-15\t16-20\t21-25\n1s\t2s\t5s\t10s\t20s",
                    "entryslider",
                    5,
                    {
                        "min" : 1,
                        "max" : 25,
                        "entry_width" : 24,
                        "slider_length" : 198
                    }
                ),
                "suggested_moves_count" : Setting(
                    5, 
                    "Number of Suggested Moves", 
                    "entryslider", 
                    3,
                    {
                        "min" : 1,
                        "max" : 10,
                        "entry_width" : 24,
                        "slider_length" : 198
                    }
                )                  
            }
        ),
        "LogSettings" : Section(
            " Log Settings",
            True,
            settings= {
                "logs_per_folder" : Setting(
                    100, 
                    "Logs per Folder", 
                    "numentry",
                    2, 
                    {
                        "min" : 1,
                        "max" : 1000,
                        "entry_width" : 24
                    }
                ),
                "use_custom_path" : Setting(
                    False,
                    "Use Custom Path",
                    "dropdown",
                    2,
                    {"dropdown_options" : ["True", "False"]}
                ),
                "custom_path" : Setting(
                    "C:/", 
                    "Pick custom Path", 
                    "pickdir",
                    2, 
                    {"button_text" : "Open"}
                )
            }
        )
    } 

    default_settings = {
        section_name: {setting_name: setting_data.default_value for setting_name, setting_data in section_data.settings.items()}
        for section_name, section_data in settings_structure.items()
    }
    
    @classmethod
    def create_default(cls):
        """Create settings file if not made."""
        config = configparser.ConfigParser()
        config.read_dict(cls.default_settings)
        with open("settings.ini", 'w') as settings_file:
            config.write(settings_file)
            
    @classmethod
    def load_settings(cls):
        """Read the settings from the file into a dictionary."""
        config = configparser.ConfigParser()
        with open("settings.ini", 'r') as settings_file:
            config.read_file(settings_file)
            settings_dict = copy.deepcopy(cls.default_settings)
            # For each setting copy its value from the file into a dictionary while preserving the type of value
            for section_name, section_dict in settings_dict.items():
                for setting_name, setting_value in section_dict.items():
                    if type(setting_value) is int:
                        settings_dict[section_name][setting_name] = config.getint(section_name, setting_name)
                    elif type(setting_value) is float:
                        settings_dict[section_name][setting_name] = config.getfloat(section_name, setting_name)
                    elif type(setting_value) is bool:
                        settings_dict[section_name][setting_name] = config.getboolean(section_name, setting_name)
                    else: # Assume type is str
                        settings_dict[section_name][setting_name] = config.get(section_name, setting_name)
            return settings_dict
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Settings.ico")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.minsize(200, 100)
        self.title("Settings")
        
        # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()
        
        # Read settings file
        self.config = configparser.ConfigParser()
        with open("settings.ini", 'r') as settings_file:
            self.config.read_file(settings_file)

        # Creating settings GUI elements
        settings_frame = tk.Frame(self)
        settings_frame.pack(padx=5, pady=5)
        max_section_height = 12
        self.tk_vars: dict[str, dict[str, tk.Variable]] = {}
        # Go through the dictionary with details on how the settings should be made
        for section_name, section_data in type(self).settings_structure.items():
            if section_data.public_setting: # If settings should be able to be changed easily by users
                self.tk_vars[section_name] = {}
                section_frame = self._make_section_frame(settings_frame, section_data.display_name)
                # Simple guess at the height of a column of settings so that a sections gets broken up into multiple collumns if long enough
                section_height = 0 
                for setting_name, setting_data in section_data.settings.items():
                    # Make the correct tk variable
                    if type(setting_data.default_value) is int:
                        setting_var = tk.IntVar(value= self.config.getint(section_name, setting_name))
                    elif type(setting_data.default_value) is float:
                        setting_var = tk.DoubleVar(value= self.config.getfloat(section_name, setting_name))
                    elif type(setting_data.default_value) is bool:
                        setting_var = tk.BooleanVar(value= self.config.getboolean(section_name, setting_name))
                    else: # Assume type is str
                        setting_var = tk.StringVar(value= self.config.get(section_name, setting_name))
                    self.tk_vars[section_name][setting_name] = setting_var
                    # Make the GUI based on the defined structure
                    if section_height + setting_data.height > max_section_height: # If you need more space make it
                        section_frame = self._make_section_frame(settings_frame, section_data.display_name)
                    tk.Label(section_frame, text= setting_data.display_name).pack(padx=5, pady=5)
                    # Add correct widget
                    if setting_data.widget_type == "entryslider":
                        setting_entry = tk.Entry(section_frame, width=setting_data.options["entry_width"], textvariable=setting_var)
                        setting_entry.pack(side=tk.TOP, padx=10, pady=(5,0))
                        setting_slider = tk.Scale(section_frame, variable=setting_var, from_=setting_data.options["min"], to=setting_data.options["max"], orient=tk.HORIZONTAL, length=setting_data.options["slider_length"])
                        setting_slider.pack(side=tk.TOP, padx=10, pady=5)
                    elif setting_data.widget_type == "numentry":
                        setting_entry = tk.Entry(section_frame, width=setting_data.options["entry_width"], textvariable=setting_var)
                        setting_entry.pack(side=tk.TOP, padx=10, pady=(5,0))
                        # Invisible slider to force the entry box to respect an numerical input range
                        setting_slider = tk.Scale(section_frame, variable=setting_var, from_=setting_data.options["min"], to=setting_data.options["max"], orient=tk.HORIZONTAL)
                    elif setting_data.widget_type == "dropdown":
                        if type(setting_data.default_value) is str:
                            setting_dropdown = tk.OptionMenu(section_frame, setting_var, *setting_data.options["dropdown_options"])
                        else:
                            temp_var = tk.StringVar(value=str(setting_var.get()))
                            setting_dropdown = tk.OptionMenu(section_frame, temp_var, *setting_data.options["dropdown_options"])
                            if type(setting_data.default_value) is int:
                                callbackfunc = lambda *args, str_var = temp_var, real_var = setting_var: self._save_to_int(*args, str_var, real_var)
                            elif type(setting_data.default_value) is float:
                                callbackfunc = lambda *args, str_var = temp_var, real_var = setting_var: self._save_to_float(*args, str_var, real_var)
                            else: # Assume type is bool
                                callbackfunc = lambda *args, str_var = temp_var, real_var = setting_var: self._save_to_bool(*args, str_var, real_var)
                            temp_var.trace_add('write', callbackfunc)
                        setting_dropdown.pack(side=tk.TOP, padx=10, pady=5)
                    elif setting_data.widget_type == "pickdir":
                        setting_button = tk.Button(section_frame, text=setting_data.options["button_text"], command=lambda: self.choose_dir(setting_var, os.path.dirname(os.path.abspath(__file__))))
                        setting_button.pack(padx=10, pady=5)
                    else: # Widget isn't implmented # Does this need a stronger warning?
                        tk.Label(section_frame, text= f"widget {setting_data.widget_type} is not implemented for the settings GUI").pack(side=tk.TOP, padx=5, pady=5)
                    

        # Save, cancel and reset buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, padx=10, pady=5)
        
        tk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=10, pady=5)

        # Pauses code until answered
        self.wait_window(self)
        
    
    def _make_section_frame(self, settings_frame: tk.Frame, name: str):
        """Makes a frame for a section and packs it."""
        section_frame = tk.Frame(settings_frame)
        tk.Label(section_frame, text= name, font=("TkDefaultFont", 14)).pack(side=tk.TOP, padx=5, pady=10)
        section_frame.pack(side=tk.LEFT, padx=10, pady=5)
        return section_frame

    def save(self):
        # Read values in settings GUI
        for section_name, section_data in type(self).settings_structure.items():
            if section_data.public_setting:
                for setting_name, setting_data in section_data.settings.items():
                    self.config[section_name][setting_name] = str(self.tk_vars[section_name][setting_name].get())
        # Save to file
        with open("settings.ini", 'w') as settings_file:
            self.config.write(settings_file) 
        self.close()
        
    def cancel(self): 
        self.close()
        
    def reset(self):
        if self.settings_yes_no("Reset to default values?").result:
            # Reset GUI values
            for section_name, section_data in type(self).settings_structure.items():
                if section_data.public_setting:
                    for setting_name, setting_data in section_data.settings.items():
                        self.tk_vars[section_name][setting_name].set(type(self).default_settings[section_name][setting_name])
        
    def close(self):
        self.tk_vars.clear()
        self.destroy()
        
    def settings_yes_no(self, question_to_ask):
        return YesNoIO(
            parent=self, 
            question=question_to_ask, 
            title="Reset Settings",
            icon_path="images/icons/Settings.ico"
        )
        
    def choose_dir(self, strVar: tk.StringVar, initialdir):
        strVar.set(filedialog.askdirectory(title="Choose Directory", initialdir=initialdir, parent=self))
        
    def _save_to_bool(self, name, index, mode, str_var: tk.StringVar, bool_var: tk.BooleanVar):
        bool_var.set(str_to_bool(str_var.get()))
        
    def _save_to_int(self, name, index, mode, str_var: tk.StringVar, int_var: tk.IntVar):
        int_var.set(int(str_var.get()))
        
    def _save_to_float(self, name, index, mode, str_var: tk.StringVar, float_var: tk.DoubleVar):
        float_var.set(float(str_var.get()))
        
