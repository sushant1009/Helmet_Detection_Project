import os
os.environ['INSIGHTFACE_HOME'] = '/root/.insightface'

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from fastapi import FastAPI, UploadFile, Form, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import insightface
import traceback
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Load model from cached path
print("Loading InsightFace model...")
try:
    model = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
    model.prepare(ctx_id=-1, det_size=(640, 640))
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
    model = None


def generate_embeddings_img(image):
    try:
        logger.info(f"Image shape: {image.shape}")
        
        # Resize if too large to prevent memory issues
        max_dimension = 1920
        height, width = image.shape[:2]
        
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.info(f"Resized image to: {image.shape}")
        
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces
        logger.info("Detecting faces...")
        faces = model.get(img_rgb)
        logger.info(f"Found {len(faces) if faces else 0} faces")

        if not faces or len(faces) == 0:
            logger.warning("No face detected in the given image.")
            return None

        # Use the first detected face
        face = faces[0]
        emb = face.embedding.astype('float32')
        logger.info(f"Generated embedding with shape: {emb.shape}")
        
        return emb
    
    except Exception as e:
        logger.error(f"Error in generate_embeddings_img: {str(e)}")
        logger.error(traceback.format_exc())
        raise


@app.get("/")
async def root():
    return {"message": "Face Embeddings Generator API is running"}


@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "model_loaded": model is not None
    }


@app.post("/get-embeddings")
async def generate_embeddings(file: UploadFile = File(...)):
    logger.info(f"Received request for file: {file.filename}")
    
    try:
        # Check if model is loaded
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Read file contents
        logger.info("Reading file contents...")
        contents = await file.read()
        logger.info(f"File size: {len(contents)} bytes")
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if len(contents) > max_size:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB")
        
        # Validate file is not empty
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file received")
        
        # Decode image
        logger.info("Decoding image...")
        img_data = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("Failed to decode image")
            raise HTTPException(status_code=400, detail="Could not read image. Invalid format.")

        logger.info(f"Image decoded successfully. Shape: {img.shape}")

        # Generate embedding
        logger.info("Generating embedding...")
        embedding = generate_embeddings_img(img)

        if embedding is None:
            raise HTTPException(status_code=404, detail="No face detected in image")

        logger.info("Embedding generated successfully")
        
        return {
            "success": True,
            "embedding": embedding.tolist(),
            "embedding_size": len(embedding)
        }

    except HTTPException as he:
        logger.warning(f"HTTP Exception: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        try:
            await file.close()
            logger.info("File closed")
        except:
            pass


