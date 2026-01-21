import os
import cv2
import faiss
import numpy as np
import insightface
import pymongo
import threading
import traceback
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

VIOLATION_THRESHOLD = timedelta(minutes=1)

violation_tracker = {
  
}

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

load_dotenv()

EMBED_DIM = int(os.getenv("EMBED_DIM", 512))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.35))

mongo_client = pymongo.MongoClient(
    f"mongodb://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
)
db = mongo_client[os.getenv("DB_NAME")]
embeddings_col = db["embeddings"]
users_col = db["users"]

face_model = insightface.app.FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)
face_model.prepare(ctx_id=-1, det_size=(640, 640))
print("InsightFace loaded")

_index_lock = threading.Lock()
_faiss_index = None
_user_ids = []
_user_names = []
_user_emails = []

def send_violation_email(name, user_id, score,v_email):
    msg = MIMEText(
        f"""
Helmet violation detected.

Name: {name}
User ID: {user_id}
Confidence: {score:.2f}

Violation duration exceeded 3 minutes.
"""
    )

    msg["Subject"] = "Safety Helmet Violation Alert"
    msg["From"] = SENDER_EMAIL
    msg["To"] = v_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

    print(f"Email sent for {name}")


def load_embeddings():
    global _faiss_index, _user_ids, _user_names,_user_emails

    vectors = []
    ids = []
    names = []
    emails = []

    for doc in embeddings_col.find():
        emb = np.array(doc["embedding"], dtype="float32")
        emb = emb / np.linalg.norm(emb)

        user = users_col.find_one({"user_id": doc["user_id"]})
        name = user.get("full_name", doc["user_id"])
        email = user.get("email", doc["user_id"])
        vectors.append(emb)
        ids.append(doc["user_id"])
        names.append(name)
        emails.append(email)

    if not vectors:
        _faiss_index = faiss.IndexFlatIP(EMBED_DIM)
        return

    vectors = np.vstack(vectors)

    _faiss_index = faiss.IndexFlatIP(EMBED_DIM)
    _faiss_index.add(vectors)

    _user_ids = ids
    _user_names = names
    _user_emails = emails

    print(f"FAISS loaded with {_faiss_index.ntotal} embeddings")

load_embeddings()

def search_embedding(embedding):
    with _index_lock:
        D, I = _faiss_index.search(
            embedding.reshape(1, -1).astype("float32"), 1
        )

    score = float(D[0][0])
    idx = int(I[0][0])

    if idx < 0 or score < SIMILARITY_THRESHOLD:
        return {
            "label": "Unknown",
            "user_id": None,
            "score": score
        }

    return {
        "label": _user_names[idx],
        "user_id": _user_ids[idx],
        "email": _user_emails[idx],
        "score": score
    }

def face_inside_head(face_box, head_box):
    fx1, fy1, fx2, fy2 = face_box
    hx1, hy1, hx2, hy2 = head_box

    cx = (fx1 + fx2) // 2
    cy = (fy1 + fy2) // 2

    return hx1 <= cx <= hx2 and hy1 <= cy <= hy2

def process_helmet_detection(frame, detections):

    heads = []
    helmets = []

    for det in detections:
        if det["label"] == "no_helmet":
            heads.append(det)
        elif det["label"] == "helmet":
            helmets.append(det)

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

        now = datetime.utcnow()

    for v in violations:
        uid = v["user_id"]

        if uid is None:
            continue

        if uid not in violation_tracker:
            violation_tracker[uid] = {
                "start_time": now,
                "alert_sent": False
            }
            continue

        elapsed = now - violation_tracker[uid]["start_time"]
        print(elapsed)

        if elapsed >= VIOLATION_THRESHOLD and not violation_tracker[uid]["alert_sent"]:
            send_violation_email(
                v["name"],
                uid,
                v["score"],
                v['email']
            )
            violation_tracker[uid]["alert_sent"] = True

        
        for h in heads:
            x1, y1, x2, y2 = map(int, (h["x1"], h["y1"], h["x2"], h["y2"]))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, "NO HELMET", (x1, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Draw helmets
        for h in helmets:
            x1, y1, x2, y2 = map(int, (h["x1"], h["y1"], h["x2"], h["y2"]))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "HELMET", (x1, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255,0), 2)
            
        active_user_ids = {v["user_id"] for v in violations if v["user_id"]}

        for uid in list(violation_tracker.keys()):
            if uid not in active_user_ids:
                del violation_tracker[uid]



    return frame, {
            "total_heads": len(heads),
            "helmet_violations": len(violations),
            "violators": violations
        }
