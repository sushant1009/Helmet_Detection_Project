import os
os.environ['INSIGHTFACE_HOME'] = '/root/.insightface'  # ADD THIS BEFORE importing insightface

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from fastapi import FastAPI, UploadFile, Form, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import insightface

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model from cached path
print("Loading InsightFace model...")
model = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
model.prepare(ctx_id=-1, det_size=(640, 640))
print("Model loaded successfully!")


def generate_embeddings_img(image):
    # No need to convert to RGB - insightface expects BGR
    faces = model.get(image)

    if not faces or len(faces) == 0:
        print("No face detected in the given image.")
        return None

    face = faces[0]
    emb = face.embedding
    emb = emb / np.linalg.norm(emb)  # Normalize

    return emb


@app.get("/")
async def root():
    return {"message": "Face Embeddings Generator API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": True}


@app.post("/get-embeddings")
async def generate_embeddings(
    file: UploadFile = File(...)
):
    try:
        img_data = np.frombuffer(await file.read(), np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Could not read image")

        embedding = generate_embeddings_img(img)

        if embedding is None:
            raise HTTPException(status_code=404, detail="No face detected in image")

        return {
            "embedding": embedding.tolist()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


