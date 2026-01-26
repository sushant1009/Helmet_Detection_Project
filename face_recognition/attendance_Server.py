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
import numpy as np
import insightface
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
from typing import List, Tuple
from datetime import datetime, date, timedelta
from pymongo import MongoClient
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError

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
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD"))
_index_lock = threading.Lock()
_worker_id = []
_supervisor_id = []
_worker_names = []
_worker_email = []
_supervisor_email = []
embeddings = []
_faiss_index: faiss.Index = None
_index_loaded = False
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def load_data_from_db():
    conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USERNAME"),
    password=os.getenv("PG_PASSWORD"),
    port=os.getenv("PG_PORT")   
)   

    mongo_client = pymongo.MongoClient(
        f"mongodb://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    )
    db = mongo_client[os.getenv("DB_NAME")]
    embeddings_col = db["embeddings"]

    cursor = conn.cursor()

    supervisorId = 1;

    query = """
    SELECT w.worker_id,w.full_name,w.email,w.supervisor_id,s.email
    FROM workers w join supervisor s
    ON w.supervisor_id = s.supervisor_id
    WHERE w.supervisor_Id = %s;
    """
    
    cursor.execute(query, (supervisorId,))
    rows = cursor.fetchall()

    for row in rows:
        print(f"w.worker_id : {row[0]} w.full_name : {row[1]}, w.email : {row[2]}, w.supervisor_id : {row[3]}, s.email : {row[4]}")
        doc = embeddings_col.find_one(
        {
            "workerId": str(row[0]),
            "supervisorId": str(row[3])
        },
        {"embedding": 1, "_id": 0}
        )

        if doc:
          emb = doc["embedding"]
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

def mark_attendance(user_id: str, update_threshold: int = 5):
    print("Marked for ",user_id)

    # today_str = date.today().isoformat()
    # now = datetime.utcnow()

    # record = attendance_col.find_one({"user_id": user_id, "date": today_str})

    # if record:
    #     entry_time = record.get("entry_time", now)
    #     last_seen = record.get("last_seen", now)

        
    #     if (now - last_seen) >= timedelta(minutes=update_threshold):
    #         worked_time = round((now - entry_time).total_seconds() / 3600, 2)  # hours

    #         attendance_col.update_one(
    #             {"user_id": user_id, "date": today_str},
    #             {
    #                 "$set": {
    #                     "last_seen": now,
    #                     "worked_time": worked_time
    #                 }
    #             }
    #         )
    #         print(f"[INFO] Updated attendance for {user_id} at {now}")
    #     else:
    #         print(f"[SKIP] Skipping update for {user_id}, too soon since last update.")
    # else:
    #     # First appearance today
    #     attendance_col.insert_one({
    #         "user_id": user_id,
    #         "date": today_str,
    #         "entry_time": now,
    #         "last_seen": now,
    #         "worked_time": 0
    #     })
    #     print(f"[INFO] New attendance entry for {user_id} at {now}")



def load_faiss_index(embeddings_list):
    """
    embeddings_list: List[List[float]]  (e.g. 512-d vectors)
    returns: faiss.Index
    """
    if len(embeddings_list) == 0:
        raise ValueError("No embeddings found to build FAISS index")

    # Convert to numpy float32
    vectors = np.array(embeddings_list).astype("float32")

    dim = vectors.shape[1]  # 512
    index = faiss.IndexFlatL2(dim)  # L2 distance

    index.add(vectors)  # add all embeddings
    print("FAISS index loaded with", index.ntotal, "vectors")

    return index

load_data_from_db()
_faiss_index = load_faiss_index(embeddings)
_index_loaded = True

def _search_embedding(emb: np.ndarray, bbox: np.ndarray) -> dict:
    """
    Synchronous function that queries FAISS index and returns a detection dict.
    """
    global _faiss_index, _worker_id, _worker_names
    if _faiss_index is None or _faiss_index.ntotal == 0:
        # no known faces
        return {
            "label": "Unknown",
            "score": 0.0,
            "x1": int(bbox[0]), "y1": int(bbox[1]), "x2": int(bbox[2]), "y2": int(bbox[3])
        }

    # protect index with lock because FAISS is not thread-safe for simultaneous writes; reads are usually safe but we lock
    with _index_lock:
        D, I = _faiss_index.search(emb.reshape(1, -1).astype('float32'), 1)
        score = float(D[0][0])
        idx = int(I[0][0])
        if idx < 0 or idx >= len(_worker_id):
            label = "Unknown"
        else:
            candidate_id = _worker_id[idx]
            candidate_name = _worker_names[idx] if idx < len(_worker_names) else candidate_id
            if score >= SIMILARITY_THRESHOLD:
                label = candidate_name  # or return candidate_id if you prefer
            else:
                label = "Unknown"
    return {
        "label": label,
        "user_id":candidate_id,
        "score": score,
        "x1": int(bbox[0]), "y1": int(bbox[1]), "x2": int(bbox[2]), "y2": int(bbox[3])
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

    recognized_session = set()
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
                print(f"Sent annotated frame with {len(detections)} detections")
            except Exception as e:
                print("Failed to send payload:", e)
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
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("attendance_Server:app", host="0.0.0.0", port=8000, reload=True)



