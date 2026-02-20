"""
REST endpoints for the helmet monitoring service.

  POST /helmet-monitoring/reload_index    -reload worker embeddings
  GET  /helmet-monitoring/status         - active camera sessions + system health
"""
from __future__ import annotations

import psycopg2
from fastapi import APIRouter, Header, HTTPException

from utils.auth import verify_jwt
from config import PG_DSN
from services.face_recognition import face_service
from services.camera_session import session_manager
from database.postgres import get_db_cursor

router = APIRouter(prefix="/helmet-monitoring")


@router.post("/reload_index")
async def reload_index(authorization: str = Header(...)):
    """
    Reload face embeddings for the authenticated supervisor and rebuild
    the FAISS index.  Requires a SUPERVISOR role JWT.
    """
    # ── Auth ──────────────────────────────────────────────────────────────────
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.removeprefix("Bearer ").strip()
    payload, err = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail=err or "Invalid or expired token")

    if payload.get("role") != "SUPERVISOR":
        raise HTTPException(status_code=403, detail="Only SUPERVISOR role may reload the index")

    # ── Resolve supervisor_id from email ──────────────────────────────────────
    supervisor_email = payload.get("sub")
    supervisor_id = _get_supervisor_id(supervisor_email)
    if supervisor_id is None:
        raise HTTPException(status_code=404, detail="Supervisor not found")

    # ── Reload ────────────────────────────────────────────────────────────────
    try:
        count = face_service.reload_for_supervisor(supervisor_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return {
        "message": "Index reloaded successfully",
        "supervisor_id": supervisor_id,
        "workers_loaded": count,
    }


@router.get("/status")
async def status():
    """Return active camera sessions and whether the FAISS index is ready."""
    return {
        "index_loaded": face_service.is_loaded,
        "active_cameras": session_manager.count(),
        "sessions": session_manager.all_statuses(),
    }


# ── DB helper ─────────────────────────────────────────────────────────────────

def _get_supervisor_id(email: str) -> int | None:

    try:
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT supervisor_id FROM supervisor WHERE email = %s;",
                (email,),
            )
            row = cur.fetchone()
            return row[0] if row else None
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error while fetching supervisor ID")  