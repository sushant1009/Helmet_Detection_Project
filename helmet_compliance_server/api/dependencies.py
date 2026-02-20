"""
Shared FastAPI dependencies and application-level state.

The YOLO model is loaded once at startup and accessed through get_yolo_model()
to keep the WebSocket router free of circular imports.
"""
from __future__ import annotations

_yolo_model = None


def set_yolo_model(model) -> None:
    global _yolo_model
    _yolo_model = model


def get_yolo_model():
    if _yolo_model is None:
        raise RuntimeError("YOLO model has not been loaded yet.")
    return _yolo_model