import asyncio
import traceback
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from database.postgres import get_db_cursor
from database.mongodb import close_mongo_client
from utils.auth import verify_jwt
from services.faiss_service import faiss_service
from websocket.handlers import frame_producer, frame_consumer, rtsp_frame_producer
from config import FRAME_QUEUE_MAXSIZE
from utils.logger import setup_logger

app = FastAPI()
logger = setup_logger("app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_event():
    close_mongo_client()
    logger.info("Application shutdown complete")


@app.websocket("/ws/attendance")
async def websocket_attendance(ws: WebSocket):
    """
    WebSocket endpoint for real-time face recognition.

    Query params:
      token     — JWT (required)
      rtsp_url  — RTSP stream URL (optional). If provided, backend reads the
                  camera directly (CCTV mode). Otherwise the client sends
                  frames (webcam mode).
      fps       — frames per second for CCTV mode (optional, default 1)
    """
    token    = ws.query_params.get("token")
    rtsp_url = ws.query_params.get("rtsp_url")          # None = webcam mode
    fps      = int(ws.query_params.get("fps", "1"))     # CCTV capture rate

    # ── Auth ─────────────────────────────────────────────────────────────────
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
    logger.info(f"WebSocket authenticated: {payload} | mode: {'CCTV' if rtsp_url else 'webcam'}")

    # ── Init FAISS index ─────────────────────────────────────────────────────
    if not faiss_service.is_loaded:
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT supervisor_id FROM supervisor WHERE email = %s;",
                    (payload["sub"],),
                )
                row = cursor.fetchone()
                if not row:
                    await ws.send_json({"error": "Supervisor not found"})
                    await ws.close(code=1008)
                    return
                supervisor_id = row[0]
                logger.info(f"Initializing index for supervisor: {supervisor_id}")
                await faiss_service.initialize_index(supervisor_id)
        except Exception as e:
            logger.error(f"Error initializing index: {e}")
            traceback.print_exc()
            await ws.send_json({"error": "Failed to initialize face recognition"})
            await ws.close(code=1011)
            return

    # ── Queue + producer/consumer ─────────────────────────────────────────────
    frame_queue = asyncio.Queue(maxsize=FRAME_QUEUE_MAXSIZE)

    try:
        if rtsp_url:
            # CCTV mode — backend opens RTSP stream, client just receives frames
            logger.info(f"CCTV mode: connecting to {rtsp_url} @ {fps} fps")
            await asyncio.gather(
                rtsp_frame_producer(rtsp_url, frame_queue, fps=fps),
                frame_consumer(ws, frame_queue, token, faiss_service.search_embedding),
            )
        else:
            # Webcam mode — client sends frames, backend processes them
            logger.info("Webcam mode: waiting for client frames")
            await asyncio.gather(
                frame_producer(ws, frame_queue),
                frame_consumer(ws, frame_queue, token, faiss_service.search_embedding),
            )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        traceback.print_exc()
        try:
            await ws.send_text(json.dumps({"error": "Internal server error"}))
        except Exception:
            pass
    finally:
        await ws.close()
        logger.info("WebSocket closed cleanly")


@app.post("/attendance/reload_index")
async def reload_index(authorization: str = Header(...)):
    """Reload FAISS index with latest data"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]
    payload, _ = verify_jwt(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("role") != "SUPERVISOR":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        await faiss_service.reload_index()
        logger.info("FAISS index reloaded successfully")
        return {"message": "Index reloaded successfully"}
    except Exception as e:
        logger.error(f"Error reloading index: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload index")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=False)