import os
import json
import base64
import traceback
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from model_loader import load_model
import asyncio
from Recognize import process_helmet_detection




save_dir = "heads/"
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
device = None
frame_queue = asyncio.Queue(maxsize=7)

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


@app.websocket("/ws/helmet-monitoring")
async def websocket_attendance(ws: WebSocket):
    await ws.accept()
    print("WebSocket connection accepted")

    async def frame_processor():
        while True:
            frame = await frame_queue.get()

            try:
                detections = await recognize_frame_and_search(frame)

                frame, helmet_data = await asyncio.to_thread(
                    process_helmet_detection, frame, detections
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
            # ---------- RECEIVE ----------
            try:
                raw = await ws.receive_text()
            except WebSocketDisconnect:
                print("⚠️ Client disconnected")
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

    except Exception as e:
        print("❌ WebSocket fatal error:", e)
        traceback.print_exc()

    finally:
        processor_task.cancel()
        try:
            await ws.close()
        except:
            pass
        print("🔒 WebSocket closed cleanly")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Helmet_Monitoring:app", host="0.0.0.0", port=8003, reload=True)
