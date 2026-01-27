import os
import cv2
import faiss
import numpy as np
import insightface
import pymongo
import threading
import psycopg2
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

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD"))
ATTENDANCE_URL = os.getenv("ATTENDANCE_URL")
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
        "label": _worker_names[idx],
        "user_id": _worker_id[idx],
        "email": _worker_email[idx],
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
