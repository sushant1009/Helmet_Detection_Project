"""
WebSocket endpoint for helmet monitoring.

URL: /ws/helmet-monitoring/{camera_id}?token=<jwt>

"""
from __future__ import annotations
import asyncio
import base64
import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.auth import verify_jwt
from services.camera_session import CameraSession, session_manager, run_frame_processor
from services.face_recognition import face_service
router = APIRouter()


@router.websocket("/ws/helmet-monitoring/{camera_id}")
async def websocket_helmet_monitoring(ws: WebSocket, camera_id: str):
    # ── 1. Authenticate ───────────────────────────────────────────────────────
    token = ws.query_params.get("token")
    await ws.accept()

    if not token:
        await ws.send_json({"error": "Missing token"})
        await ws.close(code=1008)
        return

    payload, error = verify_jwt(token)
    if not payload:
        await ws.send_json({"error": error})
        await ws.close(code=1008)
        return

    if not face_service.is_loaded:
        await ws.send_json(
            {"error": "Embeddings not loaded. Call /helmet-monitoring/reload_index first."}
        )
        await ws.close(code=1008)
        return

    # ── 2. Create session ─────────────────────────────────────────────────────
    from api.dependencies import get_yolo_model   # late import to avoid circular
    yolo_model = get_yolo_model()

    supervisor_id = payload.get("supervisorId", 0)
    session = CameraSession(
        camera_id=camera_id,
        ws=ws,
        auth_token=token,
        supervisor_id=supervisor_id,
    )
    session_manager.register(session)

    processor_task = asyncio.create_task(
        run_frame_processor(session, yolo_model)
    )

    # ── 3. Receive frames
    try:
        while True:
            try:
                raw = await ws.receive_text()
            except WebSocketDisconnect:
                break

            img_b64 = _extract_b64(raw)
            if not img_b64:
                continue

            frame = _decode_frame(img_b64)
            if frame is None:
                continue

            # Drop oldest frame when queue is full 
            if session.frame_queue.full():
                try:
                    session.frame_queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass

            await session.frame_queue.put(frame)

    finally:
        processor_task.cancel()
        session_manager.unregister(camera_id)
        if ws.application_state not in (None,):
            try:
                await ws.close()
            except Exception:
                pass
        print(f"[WS] Camera '{camera_id}' WebSocket closed cleanly.")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_b64(raw: str) -> str | None:
    """Return the base-64 image string from either a JSON envelope or raw b64."""
    import json as _json
    try:
        data = _json.loads(raw)
        img_b64 = data.get("image", "")
    except Exception:
        img_b64 = raw

    if not img_b64:
        return None
    if "," in img_b64:
        img_b64 = img_b64.split(",", 1)[1]
    return img_b64


def _decode_frame(img_b64: str) -> np.ndarray | None:
    try:
        img_bytes = base64.b64decode(img_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception:
        return None