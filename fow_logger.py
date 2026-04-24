from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_settings import GameSettings

import time
import shutil
from pathlib import Path

class FowLogger:
    def __init__(self, settings: GameSettings):
        self.settings = settings
        # Define the storage path
        if self.settings.use_custom_log_path:
            current_directory = f"{self.settings.custom_log_path}/"
        else:  
            current_directory = "" 
        archive_folder_path = Path(f"{current_directory}Archived Logs")
        archive_folder_path.mkdir(exist_ok=True)
        # Count the zipped folders stored
        archive_folder_count = sum(1 for entry in archive_folder_path.iterdir())
        log_folder_path = Path(f"{current_directory}Logs")
        log_folder_path.mkdir(exist_ok=True)
        log_folder_count = sum(1 for entry in log_folder_path.iterdir())
        if log_folder_count >= self.settings.logs_per_folder:
            # zip folder and move it
            shutil.make_archive(f"{current_directory}Logs{archive_folder_count+1}", "zip", log_folder_path)
            shutil.move(f"{current_directory}Logs{archive_folder_count+1}.zip", str(archive_folder_path))
            shutil.rmtree(log_folder_path)
            # Make new log folder
            log_folder_path = Path(f"{current_directory}Logs") 
            log_folder_path.mkdir(exist_ok=True)
                
        epoch_time = int(time.time())
        self.filename = f"{log_folder_path}/{epoch_time}.log"
        pass
    
    def log(self, message):
        with open(self.filename, 'a') as logfile:
            print(message)
            print(message, file = logfile)
            
    def just_log(self, message):
        with open(self.filename, 'a') as logfile:
            print(message, file = logfile)
            
    def clear_log(self):
        with open(self.filename, 'w') as logfile:
            logfile.write("")