from src.Helmet_Detection.config.configuration import ConfigurationManager
from src.Helmet_Detection.components.Data_Transformation import DataTransformation
from src.Helmet_Detection import logger

STAGE_NAME = "Data Transformation stage"

class DataTransformationTrainingPipeline:
    def __init__(self):
        pass
    
    def main(self):
        try:
          config = ConfigurationManager()
          data_transformation_config = config.get_transformation_config()
          data_transformation = DataTransformation(config=data_transformation_config)
          data_transformation.convert_all()
          data_transformation.rename_files()
          data_transformation.train_test_val_split()

        except Exception as e :
            raise e