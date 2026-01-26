import os
import json
import base64
import threading
import traceback
import asyncio
import cv2
import numpy as np
import faiss
import pymongo
import insightface
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
from typing import List, Tuple
from datetime import datetime, date, timedelta
from pymongo import MongoClient


MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB_NAME", "face_db")
USERS_COLLECTION = os.environ.get("USERS_COLLECTION", "embeddings")
USERS_DB = os.environ.get("USERS_DB", "users")
ATTENDANCE_COLLECTION = os.environ.get("ATTENDANCE_COLLECTION", "attendance")
EMBEDDING_FIELD = "embedding"
USER_ID_FIELD = "user_id"
NAME_FIELD = "full_name"

FAISS_INDEX_PATH = os.environ.get("FAISS_INDEX_PATH", "faiss.index")  
EMBED_DIM = int(os.environ.get("EMBED_DIM", 512))                     
SIMILARITY_THRESHOLD = float(os.environ.get("SIM_THRESHOLD", 0.38))  

mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_col = db[USERS_COLLECTION]
attendance_col = db[ATTENDANCE_COLLECTION]
user_details = db[USERS_DB]


_index_lock = threading.Lock()
_faiss_index: faiss.Index = None
_user_ids: List[str] = []  
_user_names: List[str] = []
_index_loaded = False


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


def load_embeddings_from_db() -> Tuple[faiss.Index, List[str], List[str]]:
    print("Loading embeddings from MongoDB...")
    docs = list(users_col.find({}))
    if not docs:
        print("No embeddings found in DB.")
        # empty index
        idx = faiss.IndexFlatIP(EMBED_DIM)
        return idx, [], []

    # Extract embeddings and ids
    user_ids = []
    names = []
    embeddings = []
    for d in docs:
        emb = d.get(EMBEDDING_FIELD)
        uid = d.get(USER_ID_FIELD) or str(d.get("_id"))
        user = user_details.find_one({"user_id": uid})
        name = user.get(NAME_FIELD)
        print(name)
        if not emb:
            continue
        arr = np.asarray(emb, dtype='float32')
        if arr.shape[0] != EMBED_DIM:
            # skip or raise
            print(f"Skipping {uid}: embedding dimension mismatch {arr.shape}")
            continue
        # normalize
        norm = np.linalg.norm(arr)
        if norm == 0:
            continue
        arr = arr / norm
        embeddings.append(arr)
        user_ids.append(uid)
        names.append(name)

    if not embeddings:
        idx = faiss.IndexFlatIP(EMBED_DIM)
        return idx, [], []

    embeddings_np = np.vstack(embeddings).astype('float32')

    # Build FAISS index
    idx = faiss.IndexFlatIP(EMBED_DIM) 
    idx.add(embeddings_np)
    print(f"FAISS index built with {idx.ntotal} vectors")
    return idx, user_ids, names

# Initialize index at startup
def initialize_index():
    global _faiss_index, _user_ids, _user_names, _index_loaded
    with _index_lock:
        try:
            idx, ids, names = load_embeddings_from_db()
            _faiss_index = idx
            _user_ids = ids
            _user_names = names
            _index_loaded = True
        except Exception as e:
            print("Error initializing index:", e)
            traceback.print_exc()
            _faiss_index = faiss.IndexFlatIP(EMBED_DIM)
            _user_ids = []
            _user_names = []
            _index_loaded = True


initialize_index()

def add_embedding_to_index(user_id: str, name: str, embedding: List[float]):
   
    global _faiss_index, _user_ids, _user_names
    emb = np.asarray(embedding, dtype='float32')
    norm = np.linalg.norm(emb)
    if norm == 0:
        raise ValueError("Zero embedding")
    emb = emb / norm

    with _index_lock:
        if _faiss_index is None:
            _faiss_index = faiss.IndexFlatIP(EMBED_DIM)
            _user_ids = []
            _user_names = []
        _faiss_index.add(emb.reshape(1, -1))
        _user_ids.append(user_id)
        _user_names.append(name)

  
    users_col.update_one(
        {USER_ID_FIELD: user_id},
        {"$set": {USER_ID_FIELD: user_id, NAME_FIELD: name, EMBEDDING_FIELD: emb.tolist()}},
        upsert=True
    )


def mark_attendance(user_id: str, update_threshold: int = 5):

    today_str = date.today().isoformat()
    now = datetime.utcnow()

    record = attendance_col.find_one({"user_id": user_id, "date": today_str})

    if record:
        entry_time = record.get("entry_time", now)
        last_seen = record.get("last_seen", now)

        
        if (now - last_seen) >= timedelta(minutes=update_threshold):
            worked_time = round((now - entry_time).total_seconds() / 3600, 2)  # hours

            attendance_col.update_one(
                {"user_id": user_id, "date": today_str},
                {
                    "$set": {
                        "last_seen": now,
                        "worked_time": worked_time
                    }
                }
            )
            print(f"[INFO] Updated attendance for {user_id} at {now}")
        else:
            print(f"[SKIP] Skipping update for {user_id}, too soon since last update.")
    else:
        # First appearance today
        attendance_col.insert_one({
            "user_id": user_id,
            "date": today_str,
            "entry_time": now,
            "last_seen": now,
            "worked_time": 0
        })
        print(f"[INFO] New attendance entry for {user_id} at {now}")


# -------------------------
# Async wrapper for FAISS search and recognition to avoid blocking event loop
# -------------------------
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


# -------------------------
# WebSocket endpoint for attendance streaming
# -------------------------
@app.websocket("/ws/attendance")
async def websocket_attendance(ws: WebSocket):
    await ws.accept()
    print("WebSocket connection accepted")
    recognized_session = set()  # track recognized user_ids in this websocket connection/session

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
                # If not JSON, treat raw as plain base64 image
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

            # Run recognition/detection asynchronously (this function should return list of detections)
            try:
                # recognize_frame_and_search should be the async helper that returns:
                # [ { "label": ..., "score": ..., "x1":..., "y1":..., "x2":..., "y2":... }, ... ]
                detections = await recognize_frame_and_search(frame)
            except Exception as e:
                print("Error during recognition:", e)
                traceback.print_exc()
                await ws.send_text(json.dumps({"error": "recognition_failed"}))
                continue

            # mark attendance for newly recognized persons (non-blocking)
            loop = asyncio.get_running_loop()
            for det in detections:
                label = det.get("label")
                score = det.get("score", 0.0)
                user_id = det.get("user_id")
                if label and label != "Unknown" and label not in recognized_session and score >= SIMILARITY_THRESHOLD:
                    recognized_session.add(label)
                    # run mark_attendance in executor so it doesn't block
                    loop.run_in_executor(None, mark_attendance, user_id)
                    print(f"Marking attendance for {label}")

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
                print("❌ Error encoding frame:", e)
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
                print(f"✅ Sent annotated frame with {len(detections)} detections")
            except Exception as e:
                print("❌ Failed to send payload:", e)
                traceback.print_exc()
                break

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print("WebSocket loop error:", e)
        traceback.print_exc()
        try:
            await ws.close()
        except:
            pass

# -------------------------
# HTTP endpoints (reload index, health, get attendance)
# -------------------------
@app.post("/admin/reload_index")
def reload_index():
    """Reload embeddings from DB and rebuild FAISS index."""
    initialize_index()
    return {"success": True, "vectors": _faiss_index.ntotal if _faiss_index else 0}

@app.get("/admin/index_info")
def index_info():
    return {"loaded": _index_loaded, "vectors": _faiss_index.ntotal if _faiss_index else 0}

@app.get("/attendance/today")
def attendance_today(limit: int = 100):
    today_str = date.today().isoformat()
    docs = list(attendance_col.find({"date": today_str}).sort("last_seen", -1).limit(limit))
    # convert BSON datetimes to isoformat
    for d in docs:
        if "last_seen" in d:
            d["last_seen"] = d["last_seen"].isoformat()
        d.pop("_id", None)
    return docs

# -------------------------
# Optional endpoint: add single embedding (used after registration)
# -------------------------
@app.post("/admin/add_embedding")
def http_add_embedding(user_id: str, name: str, embedding_json: str):
    """
    Adds an embedding to DB and FAISS index.
    embedding_json: JSON array string or comma-separated floats.
    """
    try:
        emb_arr = json.loads(embedding_json) if embedding_json.strip().startswith("[") else [float(x) for x in embedding_json.split(",")]
    except Exception as e:
        raise HTTPException(status_code=400, detail="invalid embedding")
    add_embedding_to_index(user_id, name, emb_arr)
    return {"success": True, "user_id": user_id}

# -------------------------
# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("attendance:app", host="0.0.0.0", port=8000, reload=False)
