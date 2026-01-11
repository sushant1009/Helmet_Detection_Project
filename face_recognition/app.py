from fastapi import FastAPI, UploadFile, Form, BackgroundTasks, HTTPException,File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import pymongo
import cv2
from pydantic import BaseModel, EmailStr
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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


# OTP store
otp_store = {}

# Email credentials
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")  # Use App Password

PHOTO_DIR = "D:/userphotos"
os.makedirs(PHOTO_DIR, exist_ok=True)

def generate_user_id():
    print('0')
    count = users_col.count_documents({})
    return f"USR{count + 1:04d}"  # USR0001, USR0002, etc.

@app.post("/register")
async def register_user(
    full_name: str = Form(...),
    aadhar_no: str = Form(...),
    dob: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Generate new user ID
        user_id = generate_user_id()
        print(user_id)
        print(full_name," ",aadhar_no," ",phone," ",email)
        # Validate image type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
        print("2")
        # Read image bytes
        img_data = np.frombuffer(await file.read(), np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Could not read image")

        
        photo_path = os.path.join(PHOTO_DIR, f"{user_id}.jpg")
        cv2.imwrite(photo_path, img)

        # Generate embeddings
        embedding = embeddings_Generator.generate_Embeddings_img(img)
        # print(embedding)
        print(full_name," ",aadhar_no," ",phone," ",email," ",photo_path," ",dob," ",datetime.now())
        
       
        user_data = {
            "user_id": user_id,
            "full_name": full_name,
            "aadhar_no": aadhar_no,
            "dob": dob,
            "email": email,
            "phone": phone,
            "photo_path": photo_path,
            "created_at": datetime.now()
        }
        print("3.5")
        users_col.insert_one(user_data)
        print("4")
        # Store embeddings separately
        embeddings_col.insert_one({
            "user_id": user_id,
             "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        })
        print("5")
        return {"success": True, "message": f"User {full_name} registered successfully!", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EmailRequest(BaseModel):
    email: EmailStr


def send_email_background(email: str, otp: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = "Your OTP for Worker Registration"
        body = f"Your One-Time Password (OTP) is: {otp}\n\nPlease use this to verify your email."
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"✅ OTP {otp} sent to {email}")

    except Exception as e:
        print(f"❌ Error sending OTP to {email}: {e}")


@app.post("/send-otp")
async def send_otp(request: EmailRequest, background_tasks: BackgroundTasks):
    email = request.email
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    background_tasks.add_task(send_email_background, email, otp)
    return {"success": True, "message": "OTP sent successfully"}


@app.post("/verify-otp")
async def verify_otp(data: dict):
    email = data.get("email")
    otp_entered = data.get("otp")

    if not email or not otp_entered:
        raise HTTPException(status_code=400, detail="Email and OTP required")

    if otp_store.get(email) == otp_entered:
        del otp_store[email]
        return {"success": True, "message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
