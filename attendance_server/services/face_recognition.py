import cv2
import numpy as np
import asyncio
from typing import List
from insightface.app import FaceAnalysis
from utils.logger import setup_logger

logger = setup_logger("face_recognition")

# Initialize face model
logger.info("Loading InsightFace model...")  
face_model = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
face_model.prepare(ctx_id=-1, det_size=(640, 640))
logger.info("InsightFace ready")

async def recognize_frame_and_search(frame_bgr: np.ndarray, search_callback) -> List[dict]:
    """
    Detect faces in frame and search for matches
    search_callback: function that takes (embedding, bbox) and returns detection dict
    """
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    faces = face_model.get(frame_rgb)

    detections = []
    if len(faces) == 0:
        return detections

    loop = asyncio.get_running_loop()
    tasks = []
    
    for face in faces:
        bbox = face.bbox.astype(int)
        emb = face.embedding
        emb = emb / np.linalg.norm(emb)
        tasks.append(loop.run_in_executor(None, search_callback, emb, bbox))

    results = await asyncio.gather(*tasks)
    for r in results:
        if r is not None:
            detections.append(r)
    
    return detections