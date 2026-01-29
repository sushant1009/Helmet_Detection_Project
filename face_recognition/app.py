from fastapi import FastAPI, UploadFile, Form, BackgroundTasks, HTTPException,File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import pymongo
import cv2
from pydantic import BaseModel, EmailStr
from GenerateEncoding import GenerateEmbeddings
import os
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

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


# MongoDB setup
mongo_client = pymongo.MongoClient("mongodb://"+os.getenv("DB_HOST")+":"+os.getenv("DB_PORT")+"/")
db = mongo_client[os.getenv('DB_NAME')]

# Define collections
users_col = db["users"]
embeddings_col = db["embeddings"]


class EmailRequest(BaseModel):
    email: EmailStr



@app.post("/get-embeddings")
async def generate_embeddings(file: UploadFile = File(...), workerId: str = Form(...), supervisorId: str = Form(...) ):
    img_data = np.frombuffer(await file.read(), np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Could not read image")

    embedding = embeddings_Generator.generate_Embeddings_img(img)
    embeddings_col.insert_one({
            "workerId": workerId,
             "supervisorId": supervisorId,
             "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
            "created_at": datetime.now()
        })
    doc = embeddings_col.find_one({"workerId": workerId}, {"_id": 1})
    return {
        "id": str(doc["_id"])
    }

    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
