import os
from pathlib import Path
import logging
import sys

log_str = '[%(asctime)s] - %(levelname)s : %(module)s  : %(message)s'

log_dir = "logs"
logs_filepath = os.path.join(log_dir, "Running_logs.log")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(level=logging.INFO,
                    format=log_str,
                    handlers=[logging.FileHandler(logs_filepath),
                              logging.StreamHandler(sys.stdout)]
                    )
                    

logger = logging.getLogger("HELMET_DETECTION_LOGGER")

