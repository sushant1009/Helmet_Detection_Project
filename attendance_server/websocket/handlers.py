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
from utils.logger import setup_logger

logger = setup_logger("websocket_handlers")


# ─────────────────────────────────────────────────────────────────────────────
# WEBCAM MODE — client sends frames over WebSocket
# ─────────────────────────────────────────────────────────────────────────────
async def frame_producer(ws: WebSocket, queue: asyncio.Queue):
    """Receive frames from WebSocket client (webcam mode) and push to queue."""
    dropped_count = 0
    try:
        while True:
            try:
                raw = await ws.receive_text()
            except Exception as e:
                logger.info(f"Producer: WebSocket read ended — {e}")
                break

            if queue.full():
                dropped_count += 1
                logger.info(f"Producer: queue full — frame dropped (total: {dropped_count})")
                continue

            await queue.put(raw)
    finally:
        await queue.put(None)  # sentinel — tells consumer to stop


# ─────────────────────────────────────────────────────────────────────────────
# CCTV MODE — backend reads RTSP and pushes frames to queue
# ─────────────────────────────────────────────────────────────────────────────
async def rtsp_frame_producer(rtsp_url: str, queue: asyncio.Queue, fps: int = 1):
    """
    Open an RTSP stream with OpenCV, read frames at `fps` rate,
    encode them as base64 JSON strings, and push to queue.
    Runs in a thread pool so cv2 blocking calls don't stall the event loop.
    """
    logger.info(f"RTSP producer starting: {rtsp_url} @ {fps} fps")

    loop = asyncio.get_event_loop()

    def _read_rtsp():
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            logger.error(f"RTSP producer: failed to open stream — {rtsp_url}")
            return

        interval = 1.0 / max(fps, 1)
        dropped = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("RTSP producer: failed to read frame — stream may have ended")
                    break

                # Encode frame → base64 JSON string (same shape as webcam messages)
                _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                b64 = base64.b64encode(buf).decode("utf-8")
                raw = json.dumps({"image": b64})

                # Non-blocking put — drop if queue is full
                if not queue.full():
                    asyncio.run_coroutine_threadsafe(queue.put(raw), loop)
                else:
                    dropped += 1
                    if dropped % 30 == 0:
                        logger.info(f"RTSP producer: {dropped} frames dropped (queue full)")

                # Throttle to requested FPS
                import time
                time.sleep(interval)
        finally:
            cap.release()
            # Send sentinel so consumer knows to stop
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)
            logger.info("RTSP producer: stream closed")

    # Run blocking cv2 loop in thread pool, don't block event loop
    await loop.run_in_executor(None, _read_rtsp)


# ─────────────────────────────────────────────────────────────────────────────
# SHARED CONSUMER — processes frames regardless of source
# ─────────────────────────────────────────────────────────────────────────────
async def frame_consumer(
    ws: WebSocket,
    queue: asyncio.Queue,
    token: str,
    search_callback,
):
    """
    Dequeue frames, run face recognition, mark attendance,
    draw bounding boxes, and send annotated frame back over WebSocket.
    Works identically for both webcam and CCTV modes.
    """
    last_seen: Dict[int, datetime] = {}
    THRESHOLD = timedelta(minutes=10)

    while True:
        raw = await queue.get()

        if raw is None:
            logger.info("Consumer: received sentinel — shutting down")
            break

        # ── Parse JSON ───────────────────────────────────────────────────────
        try:
            data = json.loads(raw)
        except Exception:
            data = {"image": raw}

        img_b64 = data.get("image")
        if not img_b64:
            logger.warning("Consumer: no image field in received data")
            await ws.send_text(json.dumps({"error": "no image field"}))
            continue

        # Strip data-URI prefix if present (webcam canvas sometimes adds it)
        if "," in img_b64:
            try:
                img_b64 = img_b64.split(",")[1]
            except Exception:
                logger.warning("Consumer: failed to split data URI")
                await ws.send_text(json.dumps({"error": "bad image format"}))
                continue

        # ── Decode base64 → OpenCV frame ─────────────────────────────────────
        try:
            img_bytes = base64.b64decode(img_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                logger.warning("Consumer: failed to decode image")
                await ws.send_text(json.dumps({"error": "could not decode image"}))
                continue
        except Exception as e:
            logger.warning(f"Consumer: base64 decoding failed — {e}")
            await ws.send_text(json.dumps({"error": "bad base64"}))
            continue

        # ── Face recognition ─────────────────────────────────────────────────
        try:
            detections = await recognize_frame_and_search(frame, search_callback)
        except Exception as e:
            logger.error(f"Error during recognition: {e}")
            traceback.print_exc()
            await ws.send_text(json.dumps({"error": "recognition_failed"}))
            continue

        # ── Mark attendance ──────────────────────────────────────────────────
        for det in detections:
            label   = det.get("label")
            score   = det.get("score", 0.0)
            user_id = det.get("user_id")

            if label and label != "Unknown" and score >= SIMILARITY_THRESHOLD:
                now = datetime.now()
                if user_id not in last_seen:
                    last_seen[user_id] = now
                    await mark_attendance(user_id, frame, token)
                else:
                    if now - last_seen[user_id] > THRESHOLD:
                        last_seen[user_id] = now
                        await mark_attendance(user_id, frame, token)

        # ── Draw bounding boxes ──────────────────────────────────────────────
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
                    0.6, color, 2,
                )
            except Exception:
                traceback.print_exc()
                continue

        # ── Encode and send annotated frame ──────────────────────────────────
        try:
            _, buffer = cv2.imencode(".jpg", frame)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")
            await ws.send_text(json.dumps({
                "image":      frame_b64,
                "detections": detections,
                "frame_w":    int(frame.shape[1]),
                "frame_h":    int(frame.shape[0]),
            }))
        except Exception as e:
            logger.error(f"Failed to send payload: {e}")
            traceback.print_exc()
            break