import numpy as np
import cv2
import pickle
import insightface

# Load stored embeddings
with open("Encodings_ArcFace.p", "rb") as f:
    encodeList, studentIds = pickle.load(f)

encodeList = np.array(encodeList)
encodeList = encodeList / np.linalg.norm(encodeList, axis=1, keepdims=True)

# Initialize ArcFace model
model = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
model.prepare(ctx_id=-1, det_size=(640, 640))

cap = cv2.VideoCapture(0)
recognized_cache = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = model.get(frame_rgb)

    for face in faces:
        bbox = face.bbox.astype(int)
        emb = face.embedding  # ✅ use embedding directly
        emb = emb / np.linalg.norm(emb)

        # Compute cosine similarity
        sims = np.dot(encodeList, emb)
        best = np.argmax(sims)
        sim_score = sims[best]

        # Threshold tuning
        if sim_score > 0.38:  
            name = studentIds[best]
            if name not in recognized_cache:
                recognized_cache.add(name)
                print(f"Recognized {name} with score {sim_score:.2f}")

            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,255,0), 2)
            cv2.putText(frame, f"{name} ({sim_score:.2f})", (bbox[0], bbox[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        else:
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,0,255), 2)
            cv2.putText(frame, "Unknown", (bbox[0], bbox[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    cv2.imshow("Face Recognition (ArcFace)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
