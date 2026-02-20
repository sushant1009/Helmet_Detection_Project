from ultralytics import YOLO
import torch
from config import YOLO_MODEL_PATH

from utils.logger import setup_logger

MODEL_PATH = YOLO_MODEL_PATH

logger = setup_logger("model_loader")

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f" Loading YOLO model on {device.upper()}")

    model = YOLO(MODEL_PATH)
    model.to(device)

    return model, device
