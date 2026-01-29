import os
import json
import base64
import traceback
import cv2
import numpy as np
import psycopg2
import jwt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from model_loader import load_model
import asyncio
from Recognize import process_helmet_detection,set_Supervisor
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

    await ws.accept()
    print("WebSocket authenticated:", payload)

    
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USERNAME"),
        password=os.getenv("PG_PASSWORD"),
        port=os.getenv("PG_PORT")
    )

    cursor = conn.cursor()

    query = """
    SELECT supervisor_id
    FROM supervisor
    WHERE email = %s;
    """

    cursor.execute(query, (payload['sub'],))
    row = cursor.fetchone()

    if not row:
        await ws.send_json({"error": "Invalid Supervisor"})
        await ws.close(code=1008)
        return
        
    supervisor_id = row[0]
    set_Supervisor(supervisor_id,token)
    print("Supervisor ID:", supervisor_id)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Helmet_Monitoring:app", host="0.0.0.0", port=8003, reload=False)
