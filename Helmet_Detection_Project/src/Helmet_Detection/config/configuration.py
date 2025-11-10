from src.Helmet_Detection.constants import *
from src.Helmet_Detection.entity.config_entity import DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainingConfig
from src.Helmet_Detection.utils.common import read_yaml, create_directory
import os
class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH,
        params_filepath = PARAMS_FILE_PATH,
        schema_filepath = SCHEMA_FILE_PATH):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        create_directory([self.config.artifacts_root])


    
    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directory([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            source_URL=config.source_URL,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir 
        )

        return data_ingestion_config
    
    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation
        schema = self.schema.Folders
        create_directory([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir=config.root_dir,
            img_dir=config.img_dir ,
            ann_dir=config.ann_dir ,
            status_file = config.status_file,
            all_schema = schema
        )

        return data_validation_config
    
    def get_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation
        params = self.params.Data_Split
        create_directory([config.root_dir])
        data_transformation_config = DataTransformationConfig(
            root_dir = config.root_dir,
            labels_path = config.labels_dir,
            ann_path=config.ann_dir,
            img_path=config.img_dir,
            image_data_path = config.image_data_dir,
            label_data_path = config.label_data_dir,
            train_split = params.train_split,
            test_split= params.test_split,
            val_split =params.val_split 
            
        )
        
        return data_transformation_config
    
    def get_model_training_config(self) -> ModelTrainingConfig:
        config = self.config.models
        create_directory([config.root_dir])
        model_training_config = ModelTrainingConfig(
            root_dir = config.root_dir,
            model_dir= config.model_dir,
            train_data_path = config.train_data_path,
            test_data_path = config.test_data_path
        )
        
        return model_training_config