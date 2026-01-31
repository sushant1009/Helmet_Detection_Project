from ultralytics import YOLO
import torch

MODEL_PATH = "best.pt"  # change path if needed

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔥 Loading YOLO model on {device.upper()}")

    model = YOLO(MODEL_PATH)
    model.to(device)

    return model, device
