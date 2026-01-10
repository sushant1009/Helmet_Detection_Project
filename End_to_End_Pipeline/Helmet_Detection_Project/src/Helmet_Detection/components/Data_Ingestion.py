from src.Helmet_Detection import logger
from dataclasses import dataclass
from pathlib import Path
import urllib.request as request
from src.Helmet_Detection.utils.common import read_yaml, create_directory,get_size
from src.Helmet_Detection.constants import *
from src.Helmet_Detection.entity.config_entity import DataIngestionConfig
import os
import zipfile
import tarfile
import gdown

class Data_Ingestion:
    def __init__(self, config = DataIngestionConfig):
        self.config = config
    
    def download_file(self):
        
        os.makedirs(os.path.dirname(self.config.local_data_file), exist_ok=True)

        if not os.path.exists(self.config.local_data_file):
            gdown.download(
                url=self.config.source_URL,
                output=self.config.local_data_file,
                quiet=False,  # set True to suppress progress
                fuzzy=True    # allows gdrive sharing links directly
            )
            print("Download completed!")
            
        else:
             logger.info(f"File already exists of size: {get_size(Path(self.config.local_data_file))}")
    def extract_zip_file(self):
        unzip_path = self.config.unzip_dir
        file_path = self.config.local_data_file
        os.makedirs(unzip_path, exist_ok=True)
        # Detect type and extract
        try:
            # ZIP file
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(unzip_path)
                print(f"ZIP extraction completed to '{unzip_path}'!")

            # TAR file (including .tar.gz)
            elif tarfile.is_tarfile(file_path):
                with tarfile.open(file_path, 'r:*') as tar_ref:
                    tar_ref.extractall(unzip_path)
                print(f"TAR extraction completed to '{unzip_path}'!")

            else:
                raise ValueError("File is neither ZIP nor TAR. Cannot extract.")

        except Exception as e:
            raise ValueError(f"Extraction failed: {e}")
    
    


            