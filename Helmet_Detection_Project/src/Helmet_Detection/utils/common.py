import os
from box.exceptions import BoxValueError
from pathlib import Path
import logging
import sys
import yaml
import json
import joblib
from src.Helmet_Detection import logger
from box import ConfigBox
from ensure import ensure_annotations
from typing import Any

@ensure_annotations
def read_yaml(path_to_yaml : Path) -> ConfigBox:
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file : {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError(f"Empty yaml file : {path_to_yaml}")
    except Exception as  e:
        raise e 
 
@ensure_annotations
def create_directory(dirs: list,verbose=True):
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"directory created at {dir_path}")   

    
@ensure_annotations
def read_json(path_to_json : Path) -> ConfigBox:
    try:
        with open(path_to_json) as json_file:
            content = json.load(json_file)
            logger.info(f"json file : {path_to_json} loaded successfully")
            return ConfigBox(content)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid json file : {path_to_json}")
    except Exception as e:
        raise e
    
@ensure_annotations
def save_json(path :Path, data : dict):
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        logger.info(f"json file saved at : {path}")


@ensure_annotations
def get_size(path : Path)->str:
    size = round(os.path.getsize(path)/1024)
    return f"~ {size} KB"