from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataIngestionConfig :
    root_dir : Path
    source_URL : str
    local_data_file : Path
    unzip_dir : Path

@dataclass(frozen=True)
class DataValidationConfig:
    root_dir : Path
    img_dir : Path
    ann_dir : Path
    status_file : Path
    all_schema : dict 
    
@dataclass(frozen=True)
class DataTransformationConfig:
    root_dir :Path
    labels_path : Path
    ann_path : Path
    img_path : Path
    image_data_path : Path
    label_data_path : Path
    train_split : object
    test_split : object
    val_split : object
    
@dataclass(frozen=True)
class ModelTrainingConfig:
    root_dir :Path
    model_dir : Path
    train_data_path : Path
    test_data_path : Path