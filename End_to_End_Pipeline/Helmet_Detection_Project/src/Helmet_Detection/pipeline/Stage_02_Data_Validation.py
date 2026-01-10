from src.Helmet_Detection.config.configuration import ConfigurationManager
from src.Helmet_Detection.components.Data_Validation import Data_Validation
from src.Helmet_Detection import logger



STAGE_NAME = "Data Validation stage"

class DataValidationTrainingPipeline:
    def __init__(self):
        pass
    
    def main(self):
        config = ConfigurationManager()
        data_validation_config = config.get_data_validation_config()
        data_validation = Data_Validation(config = data_validation_config)
        data_validation.validate_structure()