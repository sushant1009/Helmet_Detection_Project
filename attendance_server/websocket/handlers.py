import json
import base64
import cv2
import numpy as np
import asyncio
import traceback
from typing import Dict
from datetime import datetime, timedelta
from fastapi import WebSocket
from services.face_recognition import recognize_frame_and_search
from services.attendance import mark_attendance
from config import FRAME_QUEUE_MAXSIZE, SIMILARITY_THRESHOLD

async def frame_producer(ws: WebSocket, queue: asyncio.Queue):
    """Receive frames from WebSocket and add to queue"""
    dropped_count = 0

    try:
        while True:
            try:
                raw = await ws.receive_text()
            except Exception as e:
                print(f"Producer: WebSocket read ended — {e}")
                break

            if queue.full():
                dropped_count += 1
                print(f"Producer: queue full — frame dropped (total: {dropped_count})")
                continue

            await queue.put(raw)

    finally:
        await queue.put(None)  # Sentinel value


async def frame_consumer(
    ws: WebSocket, 
    queue: asyncio.Queue, 
    token: str,
    search_callback
):
    """Process frames from queue and send results back"""
    last_seen: Dict[int, datetime] = {}
    THRESHOLD = timedelta(minutes=10)

    while True:
        raw = await queue.get()

        if raw is None:
            print("Consumer: received sentinel — shutting down")
            break

        # Parse JSON
        try:
            data = json.loads(raw)
        except Exception:
            data = {"image": raw}

        img_b64 = data.get("image")
        if not img_b64:
            await ws.send_text(json.dumps({"error": "no image field"}))
            continue

        # Strip data-URI prefix
        if "," in img_b64:
            try:
                img_b64 = img_b64.split(",")[1]
            except Exception:
                await ws.send_text(json.dumps({"error": "bad image format"}))
                continue

        # Decode base64 to frame
        try:
            img_bytes = base64.b64decode(img_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                await ws.send_text(json.dumps({"error": "could not decode image"}))
                continue
        except Exception:
            await ws.send_text(json.dumps({"error": "bad base64"}))
            continue

        # Face recognition
        try:
            detections = await recognize_frame_and_search(frame, search_callback)
        except Exception as e:
            print(f"Error during recognition: {e}")
            traceback.print_exc()
            await ws.send_text(json.dumps({"error": "recognition_failed"}))
            continue

        # Mark attendance
        for det in detections:
            label = det.get("label")
            score = det.get("score", 0.0)
            user_id = det.get("user_id")
            
            if label and label != "Unknown" and score >= SIMILARITY_THRESHOLD:
                now = datetime.now()

                if user_id not in last_seen:
                    last_seen[user_id] = now
                    await mark_attendance(user_id, token)
                    print(f"First entry for user {user_id}")
                else:
                    diff = now - last_seen[user_id]
                    if diff > THRESHOLD:
                        last_seen[user_id] = now
                        await mark_attendance(user_id, token)
                        print(f"Updated entry for user {user_id}")

        # Draw bounding boxes
        for det in detections:
            try:
                label = det.get("label", "Unknown")
                score = det.get("score", 0.0)
                x1, y1 = int(det["x1"]), int(det["y1"])
                x2, y2 = int(det["x2"]), int(det["y2"])
                
                color = (0, 255, 0) if label != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame, 
                    f"{label} : {score:.2f}", 
                    (x1, max(y1 - 6, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    color, 
                    2
                )
            except Exception:
                traceback.print_exc()
                continue

        # Encode and send frame
        try:
            _, buffer = cv2.imencode(".jpg", frame)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")
            
            response_payload = {
                "image": frame_b64,
                "detections": detections,
                "frame_w": int(frame.shape[1]),
                "frame_h": int(frame.shape[0])
            }
            
            await ws.send_text(json.dumps(response_payload))
        except Exception as e:
            print(f"Failed to send payload: {e}")
            traceback.print_exc()
            break