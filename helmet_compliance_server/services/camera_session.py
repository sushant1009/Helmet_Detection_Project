"""
Camera session manager.

Each WebSocket connection corresponds to one CameraSession.
The manager keeps a registry so the /status endpoint can report
on all active streams.
"""
from __future__ import annotations

import asyncio
import base64
import json
import threading
import traceback
from dataclasses import dataclass, field
from datetime import datetime

import cv2
import numpy as np
from starlette.websockets import WebSocketState
from fastapi import WebSocket

from config import FRAME_QUEUE_SIZE, DETECTION_CONFIDENCE
from services.helmet_detection import process_helmet_detections
from services.violation_tracker import ViolationTracker


@dataclass
class CameraSession:
    camera_id: str
    ws: WebSocket
    auth_token: str
    supervisor_id: int

    frame_queue: asyncio.Queue = field(init=False)
    violation_tracker: ViolationTracker = field(init=False)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    frames_processed: int = 0

    def __post_init__(self) -> None:
        self.frame_queue = asyncio.Queue(maxsize=FRAME_QUEUE_SIZE)
        self.violation_tracker = ViolationTracker(
            camera_id=self.camera_id,
            auth_token=self.auth_token,
        )

    def to_status(self) -> dict:
        return {
            "camera_id": self.camera_id,
            "supervisor_id": self.supervisor_id,
            "connected_at": self.connected_at.isoformat(),
            "frames_processed": self.frames_processed,
        }


class CameraSessionManager:

    def __init__(self) -> None:
        self._sessions: dict[str, CameraSession] = {}
        self._lock = threading.Lock()

    def register(self, session: CameraSession) -> None:
        with self._lock:
            self._sessions[session.camera_id] = session
        print(f"[SessionManager] Camera '{session.camera_id}' connected.")

    def unregister(self, camera_id: str) -> None:
        with self._lock:
            self._sessions.pop(camera_id, None)
        print(f"[SessionManager] Camera '{camera_id}' disconnected.")

    def all_statuses(self) -> list[dict]:
        with self._lock:
            return [s.to_status() for s in self._sessions.values()]

    def count(self) -> int:
        with self._lock:
            return len(self._sessions)


# ── Module-level singleton ────────────────────────────────────────────────────
session_manager = CameraSessionManager()


# ── Per-session frame processing loop ─────────────────────────────────────────

async def run_frame_processor(session: CameraSession, yolo_model) -> None:
    loop = asyncio.get_running_loop()

    while True:
        frame: np.ndarray = await session.frame_queue.get()
        try:
            
            annotated, detections = await _run_yolo(frame, yolo_model)

            _, helmet_data = await asyncio.to_thread(
                process_helmet_detections, frame, detections
            )

            await session.violation_tracker.process(
                helmet_data["violators"], annotated, loop
            )

            session.frames_processed += 1

            if session.ws.application_state != WebSocketState.CONNECTED:
                break

            # Encode the YOLO-annotated frame for the WebSocket stream
            _, buffer = cv2.imencode(".jpg", annotated)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")

            # face_box tuples from numpy are not JSON-serialisable — convert
            for v in helmet_data["violators"]:
                if isinstance(v.get("face_box"), tuple):
                    v["face_box"] = list(v["face_box"])

            await session.ws.send_text(
                json.dumps({"image": frame_b64, "helmet_data": helmet_data})
            )

        except asyncio.CancelledError:
            break
        except Exception:
            traceback.print_exc()


async def _run_yolo(
    frame: np.ndarray,
    model,
) -> tuple[np.ndarray, list[dict]]:

    def _infer():
        results = model(frame, conf=DETECTION_CONFIDENCE)

        annotated = results[0].plot()

        detections = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append(
                    {
                        "label": model.names[cls],
                        "score": float(box.conf[0]),
                        "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    }
                )
        return annotated, detections

    return await asyncio.to_thread(_infer)