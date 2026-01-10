from src.Helmet_Detection import logger
from src.Helmet_Detection.entity.config_entity import DataValidationConfig
from src.Helmet_Detection.utils.common import read_yaml, get_size, create_directory
from pathlib import Path
import os
import sys
import pandas as pd

class Data_Validation :
    def __init__(self, config : DataValidationConfig):
        self.config = config 
        
    def validate_structure(self) -> bool:
        validation_status = None
        folders = os.listdir(self.config.root_dir)
       
        all_folders = self.config.all_schema.keys()
        for folder in folders:
            if folder not in all_folders:
                validation_status = False 
                print(f"{folder} is not present {validation_status}")
                  
            else:
                validation_status = True
        
        with open(self.config.status_file, 'w') as f:
                    f.write(f"Validation Status : {validation_status}")
        
        return validation_status