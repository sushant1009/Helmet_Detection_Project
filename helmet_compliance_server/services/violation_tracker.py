"""
Violation tracking service.

Each camera session gets its own ViolationTracker instance so that per-worker
cooldowns are isolated to the camera that detected them.

"""
from __future__ import annotations

import asyncio
import base64
from datetime import datetime
from utils.logger import setup_logger
import cv2
import httpx
import numpy as np

from config import (
    VIOLATION_THRESHOLD,
    MAX_VIOLATIONS_BEFORE_SUPERVISOR_ALERT,
    VIOLATION_URL,
    MIN_FRAMES_BETWEEN_VIOLATIONS,
    VIOLATION_URL_SUPERVISOR
)
logger = setup_logger("services.violation_tracker")


class ViolationTracker:
  

    def __init__(self, camera_id: str, auth_token: str) -> None:
        self.camera_id = camera_id
        self._token = auth_token
        # {worker_id: {"start_time": datetime, "violation_count": int}}
        self._state: dict[int, dict] = {}

    def update_token(self, token: str) -> None:
        """Replace the auth token (e.g. after a reload)."""
        self._token = token

    async def process(
        self,
        violations: list[dict],
        annotated_frame: np.ndarray,           
        event_loop: asyncio.AbstractEventLoop,
    ) -> None:

        frame_b64: str = _encode_frame_b64(annotated_frame)

        active_ids = {v["user_id"] for v in violations if v["user_id"] is not None}
        now = datetime.utcnow()

        for v in violations:
            uid = v["user_id"]
            if uid is None:
                continue

            if uid not in self._state:
                self._state[uid] = {"start_time": now, "violation_count": 1, "frames_since_last_violation": 0}
                continue

            elapsed = now - self._state[uid]["start_time"]
            count = self._state[uid]["violation_count"]


            if (
                elapsed >= VIOLATION_THRESHOLD
                and count < MAX_VIOLATIONS_BEFORE_SUPERVISOR_ALERT
            ):
                self._state[uid]["start_time"] = now
                self._state[uid]["violation_count"] = count + 1
                self._state[uid]['frames_since_last_violation'] = 0

                asyncio.run_coroutine_threadsafe(
                    self._send_violation_notification(uid, v["score"], frame_b64,"worker"),
                    event_loop,
                )

            if self._state[uid]["violation_count"] >= MAX_VIOLATIONS_BEFORE_SUPERVISOR_ALERT:
                asyncio.run_coroutine_threadsafe(
                    self._send_violation_notification(uid, v["score"], frame_b64,"supervisor"),
                    event_loop,
                )
                self._state[uid]["violation_count"] = 0
                logger.info(
                    f"[ViolationTracker] camera={self.camera_id} worker={uid}"
                    " — supervisor alert threshold reached."
                )

        # Evict workers no longer actively violating
        for uid in list(self._state):
            if uid not in active_ids and self._state[uid]['frames_since_last_violation'] >= MIN_FRAMES_BETWEEN_VIOLATIONS:
                del self._state[uid]
            elif uid not in active_ids:
                self._state[uid]['frames_since_last_violation'] += 1
                
    async def _send_violation_notification(
        self,
        worker_id: int,
        score: float,
        frame_b64: str,
        rec:str           
    ) -> None:                    \
                                
        payload = {
            "workerId": int(worker_id),
            "score": float(score),
            "image": frame_b64,   
        }
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        try:
            if rec == "worker":
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        VIOLATION_URL, json=payload, headers=headers
                    )
                logger.info(
                    f"[ViolationTracker] Notification sent for worker={worker_id}:"
                    f" {resp.status_code}"
                )
            else:
                 async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        VIOLATION_URL_SUPERVISOR, json=payload, headers=headers
                    )
                 logger.info(
                    f"[ViolationTracker] Notification sent for worker={worker_id} to Supervisor:"
                    f" {resp.status_code}"
                )
                
        except Exception as exc:
            logger.warning(f"[ViolationTracker] HTTP error for worker={worker_id}: {exc}")


# ── Helper ────────────────────────────────────────────────────────────────────

def _encode_frame_b64(frame: np.ndarray, quality: int = 85) -> str:

    ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("cv2.imencode failed — frame may be empty or malformed.")
    return base64.b64encode(buffer).decode("utf-8")