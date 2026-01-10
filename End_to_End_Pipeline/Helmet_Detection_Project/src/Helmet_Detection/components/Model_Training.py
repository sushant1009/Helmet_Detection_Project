from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from src.Helmet_Detection.entity.config_entity import ModelTrainingConfig
from src.Helmet_Detection import logger
import pandas as pd
import joblib


class ModelTraining:
    def __init__(self, config : ModelTrainingConfig):
        self.config = config
    
    def train(self):
      
        train_data = pd.read_csv(self.config.train_data_path)
        
        X = train_data.drop('shortlisted', axis=1)  
        y = train_data['shortlisted'] 
        
        model = LinearRegression()
    
        model.fit(X, y)
        
        joblib.dump(model, self.config.model_dir)
        
        logger.info("Model training completed and saved successfully.")