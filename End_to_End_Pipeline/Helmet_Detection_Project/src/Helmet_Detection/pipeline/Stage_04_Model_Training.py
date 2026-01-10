from src.Helmet_Detection.config.configuration import ConfigurationManager
from src.Helmet_Detection.components.Model_Training import ModelTraining
from src.Helmet_Detection import logger

STAGE_NAME = "Model Training stage"

class ModelTrainingPipeline:
    def __init__(self):
        pass
    
    def main(self):
        try:
            config = ConfigurationManager()
            model_training_config = config.get_model_training_config()
            model_training = ModelTraining(config=model_training_config)
            model_training.train()
        except Exception as e :
            raise e