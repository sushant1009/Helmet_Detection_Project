import os
import psycopg2
import faiss
import pymongo
import json
import base64
import threading
import traceback
import asyncio
import cv2
import jwt
import uvicorn
import httpx
import numpy as np
import insightface
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta
from pymongo import MongoClient
from fastapi import Header, HTTPException, Depends

load_dotenv()

print("Loading InsightFace model...")
face_model = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
face_model.prepare(ctx_id=-1, det_size=(640, 640))
print("InsightFace ready")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SIMILARITY_THRESHOLD = float(os.getenv("FACE_SIMILARITY_THRESHOLD"))
ATTENDANCE_URL = os.getenv("ATTENDANCE_URL")
MONGO_URI = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_APP')}.iilebsg.mongodb.net/{os.getenv('DB_NAME')}?retryWrites=true&w=majority&appName={os.getenv('DB_APP')}"

_index_lock = threading.Lock()
_worker_id = []
_supervisor_id = []
_worker_names = []
_worker_email = []
_supervisor_email = []
embeddings = []
_faiss_index: faiss.Index = None
_index_loaded = False
Supervisor = None
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def load_data_from_db(supervisorId):
    conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USERNAME"),
    password=os.getenv("PG_PASSWORD"),
    port=os.getenv("PG_PORT"),
    sslmode="require"   
     
)  

    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[os.getenv("DB_NAME")]
    embeddings_col = db["embeddings"]

    cursor = conn.cursor()


    query = """
    SELECT w.worker_id,w.full_name,w.email,w.supervisor_id,s.email
    FROM workers w join supervisor s
    ON w.supervisor_id = s.supervisor_id
    WHERE w.supervisor_Id = %s;
    """
    
    cursor.execute(query, (supervisorId,))
    rows = cursor.fetchall()

    for row in rows:
        print(row[0]," ",row[3])
        doc = embeddings_col.find_one(
        {
            "workerId": int(row[0]),
            "supervisorId": int(row[3])
        },
        {"embeddings": 1, "_id": 0}
        )

        if doc:
          emb = doc["embeddings"]
          embeddings.append(emb)
          _worker_id.append(row[0])
          _worker_names.append(row[1])
          _worker_email.append(row[2])
          _supervisor_id.append(row[3])
          _supervisor_email.append(row[4])
        else:
            print("No matching document")


    cursor.close()
    conn.close()


async def mark_attendance(worker_id: int, token: str):
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token}"
            }

            resp = await client.post(f"{ATTENDANCE_URL}{worker_id}", headers=headers)

            print("Spring response:", resp.status_code, resp.text)
    except Exception as e:
        raise e
    
        
        


def load_faiss_index(embeddings_list):

    if len(embeddings_list) == 0:
        raise ValueError("No embeddings found to build FAISS index")

    # Convert to numpy float32
    vectors = np.array(embeddings_list).astype("float32")

    dim = vectors.shape[1]  # 512
    index = faiss.IndexFlatL2(dim)  # L2 distance

    index.add(vectors)  # add all embeddings
    print("FAISS index loaded with", index.ntotal, "vectors")

    return index



def _search_embedding(emb: np.ndarray, bbox: np.ndarray) -> dict:
    global _faiss_index, _worker_id, _worker_names

    if _faiss_index is None :
        return {
            "label": "Unknown",
            "user_id": None,
            "score": 0.0,
            "x1": int(bbox[0]), "y1": int(bbox[1]),
            "x2": int(bbox[2]), "y2": int(bbox[3])
        }

    with _index_lock:
        D, I = _faiss_index.search(emb.reshape(1, -1).astype('float32'), 1)
        score = float(D[0][0])
        idx = int(I[0][0])
        print(score)
        label = "Unknown"
        user_id = None
        if 0 <= idx < len(_worker_id):
            if score <= SIMILARITY_THRESHOLD:
                label = _worker_names[idx]
                user_id = _worker_id[idx]

    return {
        "label": label,
        "user_id": user_id,
        "score": score,
        "x1": int(bbox[0]), "y1": int(bbox[1]),
        "x2": int(bbox[2]), "y2": int(bbox[3])
    }


async def recognize_frame_and_search(frame_bgr: np.ndarray) -> List[dict]:
   
    # run face detection + embedding (InsightFace is synchronous CPU-bound)
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    faces = face_model.get(frame_rgb)

    detections = []

    if len(faces) == 0:
        return detections

    # We'll run FAISS search in thread executor as well
    loop = asyncio.get_running_loop()
    tasks = []
    for face in faces:
        bbox = face.bbox.astype(int)
        emb = face.embedding
        # normalize
        emb = emb / np.linalg.norm(emb)

        # search index in executor to avoid blocking
        tasks.append(loop.run_in_executor(None, _search_embedding, emb, bbox))

    results = await asyncio.gather(*tasks)
    for r in results:
        if r is not None:
            detections.append(r)
    return detections

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload, None

    except jwt.ExpiredSignatureError:
        return None, "Token expired"

    except jwt.InvalidSignatureError:
        return None, "Invalid token signature"

    except jwt.InvalidTokenError:
        return None, "Invalid token"


@app.websocket("/ws/attendance")
async def websocket_attendance(ws: WebSocket):
    token = ws.query_params.get("token")

    if not token:
        await ws.accept()
        await ws.send_json({"error": "Missing token"})
        await ws.close(code=1008)
        return

    payload, error = verify_jwt(token)
    if not payload:
        await ws.accept()
        await ws.send_json({"error": error})
        await ws.close(code=1008)
        return

    await ws.accept()
    print("WebSocket authenticated:", payload)
    global _index_loaded
    if not _index_loaded:
        
        conn = psycopg2.connect(
        host=os.getenv("PG_HOST"),
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USERNAME"),
        password=os.getenv("PG_PASSWORD"),
        port=os.getenv("PG_PORT"),
        sslmode="require"   
        
    )  
    
        cursor = conn.cursor()
        if(cursor):
            print("Connection Successful")
        query = """
        SELECT supervisor_id
        FROM supervisor
        WHERE email = %s;
        """

        cursor.execute(query, (payload['sub'],))
        row = cursor.fetchone()
        global Supervisor,_faiss_index
        if row:
            Supervisor = row[0]
        else:
            Supervisor = None
        print(Supervisor)
        load_data_from_db(Supervisor)
        _faiss_index = load_faiss_index(embeddings)
        _index_loaded = True
        cursor.close()

    last_seen = {}
    THRESHOLD = timedelta(minutes=10) # Min. time between attendance marking
    try:
        while True:
            # receive text (we expect JSON with {"image": "data:image/jpeg;base64,..."})
            try:
                raw = await ws.receive_text()
            except Exception as e:
                print("Error receiving from websocket:", e)
                break

            # parse incoming message
            try:
                data = json.loads(raw)
            except Exception:
                data = {"image": raw}

            img_b64 = data.get("image")
            if not img_b64:
                await ws.send_text(json.dumps({"error": "no image field"}))
                print("No image field in received message")
                continue

            # accept either "data:image/jpeg;base64,..." or plain base64
            if "," in img_b64:
                try:
                    img_b64 = img_b64.split(",")[1]
                except Exception:
                    await ws.send_text(json.dumps({"error": "bad image format"}))
                    continue

            # decode base64 -> bytes -> cv2 image
            try:
                img_bytes = base64.b64decode(img_b64)
            except Exception:
                await ws.send_text(json.dumps({"error": "bad base64"}))
                print("Bad base64 received")
                continue

            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                await ws.send_text(json.dumps({"error": "could not decode image"}))
                print("Could not decode image")
                continue

            # Face detections and recognition 
            try:
                detections = await recognize_frame_and_search(frame)
            except Exception as e:
                print("Error during recognition:", e)
                traceback.print_exc()
                await ws.send_text(json.dumps({"error": "recognition_failed"}))
                continue

            # Attendance Marking
            loop = asyncio.get_running_loop()
            for det in detections:
                label = det.get("label")
                score = det.get("score", 0.0)
                user_id = det.get("user_id")
                if label and label != "Unknown" and  score <= SIMILARITY_THRESHOLD:
                    now = datetime.now()

                    if user_id not in last_seen:
                        last_seen[user_id] = now
                        await mark_attendance(user_id, token)
                        print(f"First entry for user {user_id}")

                    diff = now - last_seen[user_id]
                  
                    if diff > THRESHOLD:
                        last_seen[user_id] = now
                        await mark_attendance(user_id, token)
                        print(f"Updated entry for user {user_id}")          

            # draw boxes & labels onto frame (so frontend can display annotated frame)
            for det in detections:
                try:
                    label = det.get("label", "Unknown")
                    x1, y1, x2, y2 = int(det["x1"]), int(det["y1"]), int(det["x2"]), int(det["y2"])
                    color = (0, 255, 0) if label != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, max(y1-6, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                except Exception:
                    # If any detection is malformed, skip drawing that box
                    traceback.print_exc()
                    continue

            # encode processed frame to jpg -> base64
            try:
                _, buffer = cv2.imencode(".jpg", frame)
                frame_b64 = base64.b64encode(buffer).decode("utf-8")
            except Exception as e:
                print(" Error encoding frame:", e)
                traceback.print_exc()
                await ws.send_text(json.dumps({"error": "frame_encoding_failed"}))
                continue

            # build payload and send
            payload = {
                "image": frame_b64,
                "detections": detections,
                "frame_w": int(frame.shape[1]),
                "frame_h": int(frame.shape[0])
            }
            try:
                await ws.send_text(json.dumps(payload))
                
            except Exception as e:
                print("Failed to send payload:", e)
                traceback.print_exc()
                break

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print("WebSocket loop error:", e)
        await ws.send_text(json.dumps({"error": f"Database Server Unavailable"}))
        traceback.print_exc()
       
    finally:
        await ws.close()
        print("WebSocket closed cleanly")
        
@app.post("/attendance/reload_index")
def reload_index(authorization: str = Header(...)):
    global embeddings, _faiss_index,_index_loaded
    global _worker_id, _worker_names, _worker_email
    global _supervisor_id, _supervisor_email

    # 1. Extract token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]

    # 2. Verify token
    payload, _ = verify_jwt(token)
    print(payload)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    role = payload.get("role")
    if role != "SUPERVISOR":
        raise HTTPException(status_code=403, detail="Not authorized")
    

    # 4. Clear old data
    embeddings.clear()
    _worker_id.clear()
    _worker_names.clear()
    _worker_email.clear()
    _supervisor_id.clear()
    _supervisor_email.clear()
    print(Supervisor)
    # 5. Reload from DB
    load_data_from_db(Supervisor)

    # 6. Rebuild FAISS
    _faiss_index = load_faiss_index(embeddings)
    _index_loaded = true
    return {"message": "Index reloaded successfully"}
    
        

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
