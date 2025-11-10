from src.Helmet_Detection.config.configuration import ConfigurationManager
from src.Helmet_Detection.components.Data_Ingestion import Data_Ingestion
from src.Helmet_Detection import logger

STAGE_NAME = "Data Ingestion"

class DataIngestionTrainingPipeline:
    def __init__(self):
        pass
    
    def main(self):
        config = ConfigurationManager()
        data_ingestion_config = config.get_data_ingestion_config()
        data_ingestion = Data_Ingestion(config=data_ingestion_config)
        data_ingestion.download_file()
        data_ingestion.extract_zip_file()