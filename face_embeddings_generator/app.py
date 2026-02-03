from fastapi import FastAPI, UploadFile, Form,HTTPException,File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from GenerateEncoding import GenerateEmbeddings
import os
from datetime import datetime
import os


app = FastAPI()
embeddings_Generator = GenerateEmbeddings()

# Allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/get-embeddings")
async def generate_embeddings(file: UploadFile = File(...), workerId: str = Form(...), supervisorId: str = Form(...) ):
    img_data = np.frombuffer(await file.read(), np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Could not read image")

    embedding = embeddings_Generator.generate_embeddings_img(img)
   
    return {
        "embedding": embedding.tolist()
    }

    

