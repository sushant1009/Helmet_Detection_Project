from ultralytics import YOLO
import torch
from config import YOLO_MODEL_PATH

MODEL_PATH = YOLO_MODEL_PATH

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f" Loading YOLO model on {device.upper()}")

    model = YOLO(MODEL_PATH)
    model.to(device)

    return model, device
