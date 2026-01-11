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
    results = model(frame, conf=0.4)

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

    
def process_helmet_detection(frame, detections):
  
    def helmet_covers_head(head_box, helmet_box):
        hx1, hy1, hx2, hy2 = head_box
        kx1, ky1, kx2, ky2 = helmet_box
        cx = (hx1 + hx2) // 2
        cy = (hy1 + hy2) // 2
        return kx1 <= cx <= kx2 and ky1 <= cy <= ky2

    heads = []
    helmets = []

    for det in detections:
        label = det.get("label")
        if label == "no_helmet":
            heads.append(det)
        elif label == "helmet":
            helmets.append(det)

    helmetless_heads = []

    for head in heads:
        h_box = (head["x1"], head["y1"], head["x2"], head["y2"])
        has_helmet = False

        for helmet in helmets:
            k_box = (helmet["x1"], helmet["y1"], helmet["x2"], helmet["y2"])
            if helmet_covers_head(h_box, k_box):
                has_helmet = True
                break

        if not has_helmet:
            helmetless_heads.append(head)

    for head in heads:
        x1, y1, x2, y2 = map(int, (head["x1"], head["y1"], head["x2"], head["y2"]))

        if head in helmetless_heads:
            color = (0, 0, 255)
            label = "NO HELMET"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        cv2.putText(frame, label, (x1, max(y1 - 6, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    for helmet in helmets:
        x1, y1, x2, y2 = map(int, (helmet["x1"], helmet["y1"], helmet["x2"], helmet["y2"]))
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
        color = (0, 255, 0)
        label = "HELMET OK"
        cv2.putText(frame, label, (x1, max(y1 - 6, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    result = {
        "total_heads": len(heads),
        "helmet_count": len(helmets),
        "helmet_violations": len(helmetless_heads),
        "violations": [
            {
                "x1": h["x1"],
                "y1": h["y1"],
                "x2": h["x2"],
                "y2": h["y2"]
            }
            for h in helmetless_heads
        ]
    }

    return frame, result


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
