import os
import json
import base64
import traceback
import cv2
import numpy as np
import psycopg2
import jwt
import asyncio
import faiss
import insightface
import threading
import psycopg2
import traceback
import asyncio
import httpx

from fastapi import FastAPI, WebSocket, WebSocketDisconnect,Header, HTTPException, Depends
from starlette.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from model_loader import load_model
from pymongo import MongoClient
from dotenv import load_dotenv

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()

model = None
device = None
frame_queue = asyncio.Queue(maxsize=7)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

violation_tracker = {
  
}


print(os.getenv("VIOLATION_THRESHOLD"))
VIOLATION_THRESHOLD = timedelta(minutes=int(os.getenv("VIOLATION_THRESHOLD")))

EMBED_DIM = int(os.getenv("EMBED_DIM", 512))
SIMILARITY_THRESHOLD = float(os.getenv("FACE_SIMILARITY_THRESHOLD"))

MONGO_URI = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_APP')}.iilebsg.mongodb.net/{os.getenv('DB_NAME')}?retryWrites=true&w=majority&appName={os.getenv('DB_APP')}"


face_model = insightface.app.FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)
face_model.prepare(ctx_id=-1, det_size=(640, 640))
print("InsightFace loaded")

# SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD"))
VIOLATION_URL = os.getenv("VIOLATION_URL")
_index_lock = threading.Lock()
_worker_id = []
supervisor_id = None
_worker_names = []
_worker_email = []
supervisor_email = None
embeddings = []
Token = None
_faiss_index: faiss.Index = None
_index_loaded = False
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")



@app.on_event("startup")
def startup_event():
    global model, device
    model, device = load_model()
   

async def recognize_frame_and_search(frame):
    results = model(frame, conf=0.35)

    detections = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            score = float(box.conf[0])

            detections.append({
                "label": label,
                "score": score,
                "x1": x1, "y1": y1, "x2": x2, "y2": y2
            })

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



async def send_violation_email(worker_id, score):
    try:
        data = {
            "workerId": int(worker_id),
            "score": float(score)
        }
        print("calling",VIOLATION_URL)

        headers = {
            "Authorization": f"Bearer {Token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                VIOLATION_URL,
                json=data,
                headers=headers
            )

        print("Spring response:", resp.status_code, resp.text)

    except Exception as e:
        print("HTTP ERROR:", e)


def load_data_from_db(supervisor_id):
    print("Loading Embeddings")
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
    SELECT worker_id,full_name,email,supervisor_id
    FROM workers
    WHERE supervisor_Id = %s;
    """
    print("Connection Successful")
    cursor.execute(query, (supervisor_id,))
    rows = cursor.fetchall()

    for row in rows:
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
          
        else:
            print("No matching document")


    cursor.close()
    conn.close()

def search_embedding(embedding):
    query = embedding.reshape(1, -1).astype("float32")
    faiss.normalize_L2(query)
    with _index_lock:
        D, I = _faiss_index.search(
            query, 1
        )

    score = float(D[0][0])
    idx = int(I[0][0])
   
    if idx < 0 or score < SIMILARITY_THRESHOLD:
        return {
            "label": "Unknown",
            "user_id": None,
            "score": score
        }
    print("Score:", score, "Idx:", _worker_names[idx])
    return {
        "label": _worker_names[idx],
        "user_id": _worker_id[idx],
        "email": _worker_email[idx],
        "score": score
    }
def load_faiss_index(embeddings_list):
    if len(embeddings_list) == 0:
        raise ValueError("No embeddings found to build FAISS index")

    vectors = np.array(embeddings_list).astype("float32")
    
    # Normalize all vectors
    faiss.normalize_L2(vectors)

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    print("FAISS index loaded with", index.ntotal, "vectors")
    return index



def face_inside_head(face_box, head_box):
    fx1, fy1, fx2, fy2 = face_box
    hx1, hy1, hx2, hy2 = head_box

    cx = (fx1 + fx2) // 2
    cy = (fy1 + fy2) // 2

    return hx1 <= cx <= hx2 and hy1 <= cy <= hy2

def process_helmet_detection(frame, detections,loop):

    heads = []
    helmets = []

    for det in detections:
        if det["label"] == "no_helmet":
            heads.append(det)
            x1, y1, x2, y2 = map(int, (det["x1"], det["y1"], det["x2"], det["y2"]))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, (f"NO HELMET" ), (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
        elif det["label"] == "helmet":
            helmets.append(det)
            x1, y1, x2, y2 = map(int, (det["x1"], det["y1"], det["x2"], det["y2"]))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "HELMET", (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255,0), 2)

    faces = face_model.get(frame)
    violations = []

    for face in faces:
        fx1, fy1, fx2, fy2 = map(int, face.bbox)
        emb = face.embedding
        emb = emb / np.linalg.norm(emb)

        for head in heads:
            hx1, hy1, hx2, hy2 = map(
                int, (head["x1"], head["y1"], head["x2"], head["y2"])
            )

            if face_inside_head((fx1, fy1, fx2, fy2), (hx1, hy1, hx2, hy2)):
                result = search_embedding(emb)
                if(result["user_id"] is not None):
                    violations.append({
                        "user_id": result["user_id"],
                        "name": result["label"],
                        "score": result["score"],
                        "email": result["email"],
                        "face_box": (fx1, fy1, fx2, fy2)
                    })
                break


    for v in violations:
        uid = v["user_id"]

        if uid is None:
            continue
        now = datetime.utcnow()
        if uid not in violation_tracker:
            violation_tracker[uid] = {
                "start_time": now,
                "violation_count": 1
            }
            continue

        elapsed = now - violation_tracker[uid]["start_time"]
        print(elapsed," count ",violation_tracker[uid]["violation_count"])

        if elapsed >= VIOLATION_THRESHOLD and violation_tracker[uid]["violation_count"] <= 5:
            violation_tracker[uid]["start_time"] = now
            violation_tracker[uid]["violation_count"] += 1
            asyncio.run_coroutine_threadsafe(send_violation_email(
                uid,
                v["score"]),loop)
            
            
        if violation_tracker[uid]["violation_count"] >= 5:
            violation_tracker[uid]["violation_count"] = 0
            print("alert supervisor")

              
    active_user_ids = {v["user_id"] for v in violations if v["user_id"]}

    for uid in list(violation_tracker.keys()):
        if uid not in active_user_ids:
            del violation_tracker[uid]



    return frame, {
            "total_heads": len(heads),
            "helmet_violations": len(violations),
            "violators": violations
        }
 


@app.websocket("/ws/helmet-monitoring")
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
    
    if(_index_loaded == False):
    
        await ws.accept()
        await ws.send_json({"Load the the Embeddings"})
        await ws.close(code=1008)
    

    await ws.accept()
    print("WebSocket authenticated:", payload)

    

    async def frame_processor():
        loop = asyncio.get_running_loop()
        while True:
            frame = await frame_queue.get()
            try:
                detections = await recognize_frame_and_search(frame)
                frame, helmet_data = await asyncio.to_thread(
                    process_helmet_detection, frame, detections,loop
                )

                _, buffer = cv2.imencode(".jpg", frame)
                frame_b64 = base64.b64encode(buffer).decode("utf-8")

                payload = {
                    "image": frame_b64,
                    "helmet_data": helmet_data
                }

                if ws.application_state == WebSocketState.CONNECTED:
                    await ws.send_text(json.dumps(payload))

            except asyncio.CancelledError:
                break
            except Exception as e:
                print("CV error:", e)
                traceback.print_exc()

    processor_task = asyncio.create_task(frame_processor())

    try:
        while True:
            try:
                raw = await ws.receive_text()
            except WebSocketDisconnect:
                print("Client disconnected")
                break

            try:
                data = json.loads(raw)
                img_b64 = data.get("image")
            except Exception:
                img_b64 = raw

            if not img_b64:
                continue

            if "," in img_b64:
                img_b64 = img_b64.split(",")[1]

            try:
                img_bytes = base64.b64decode(img_b64)
                nparr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception:
                continue

            if frame is None:
                continue

            if frame_queue.full():
                try:
                    frame_queue.get_nowait()
                    print("Extra Frames dropping")
                except asyncio.QueueEmpty:
                    pass

            await frame_queue.put(frame)

    finally:
        processor_task.cancel()
        await ws.close()
        print("WebSocket closed cleanly")
        
@app.post("/helmet-monitoring/reload_index")
async def reload_index(authorization: str = Header(...)):
  
    print("Got Call",authorization)
    # 1. Extract token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]

    # 2. Verify token
    payload, _ = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    role = payload.get("role")
    if role != "SUPERVISOR":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USERNAME"),
    password=os.getenv("PG_PASSWORD"),
    port=os.getenv("PG_PORT"),
    sslmode="require"   
     
)  

    cursor = conn.cursor()

    query = """
    SELECT supervisor_id
    FROM supervisor
    WHERE email = %s;
    """
    
    global supervisor_id, supervisor_email,embeddings, _worker_id,_worker_names, _worker_email,_faiss_index,Token,_index_loaded
    supervisor_email = payload.get("sub")
    cursor.execute(query, (payload.get("sub"),))
    row = cursor.fetchone()

    if not row:
        return {"error": "Invalid Supervisor"}
    
    supervisor_id = row[0]
    Token = token
    # 4. Clear old data
    embeddings.clear()
    _worker_id.clear()
    _worker_names.clear()
    _worker_email.clear()
   
    
    # 5. Reload from DB
    load_data_from_db(supervisor_id)

    # 6. Rebuild FAISS
    _faiss_index = load_faiss_index(embeddings)
    
    _index_loaded = True

    return {"message": "Index reloaded successfully"} 
   
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8003, reload=False)
