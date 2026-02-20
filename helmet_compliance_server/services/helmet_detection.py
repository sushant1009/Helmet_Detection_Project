"""
Helmet detection logic.

Receives raw YOLO detection dicts and the original (un-annotated) frame,
runs InsightFace on tight crops of no_helmet regions to identify violators.
"""
from __future__ import annotations

import numpy as np

from config import FACE_CROP_MODE, FACE_CROP_PADDING_PX
from services.face_recognition import face_service


def _face_inside_head(
    face_box: tuple[int, int, int, int],
    head_box: tuple[int, int, int, int],
) -> bool:
    """Return True when the face centre point is inside the head bounding box."""
    fx1, fy1, fx2, fy2 = face_box
    hx1, hy1, hx2, hy2 = head_box
    cx = (fx1 + fx2) // 2
    cy = (fy1 + fy2) // 2
    return hx1 <= cx <= hx2 and hy1 <= cy <= hy2


def _safe_crop(
    frame: np.ndarray,
    x1: int, y1: int, x2: int, y2: int,
    pad: int,
) -> tuple[np.ndarray, int, int]:
    """Crop with padding, ensuring we don't go out of frame bounds."""
    h, w = frame.shape[:2]
    cx1 = max(0, x1 - pad)
    cy1 = max(0, y1 - pad)
    cx2 = min(w, x2 + pad)
    cy2 = min(h, y2 + pad)
    return frame[cy1:cy2, cx1:cx2], cx1, cy1


def process_helmet_detections(
    frame: np.ndarray,
    detections: list[dict],
) -> tuple[None, dict]:
    
    heads: list[dict] = []
    helmets: list[dict] = []

    for det in detections:
        if det["label"] == "no_helmet":
            heads.append(det)
        elif det["label"] == "helmet":
            helmets.append(det)

    violations: list[dict] = []

    if not heads or not face_service.is_loaded:
        return None, {
            "total_heads":       len(heads),
            "total_helmets":     len(helmets),
            "helmet_violations": 0,
            "violators":         [],
        }

    if FACE_CROP_MODE:
        violations = _match_via_crops(frame, heads)
    else:
        violations = _match_via_full_frame(frame, heads)

    return None, {
        "total_heads":       len(heads),
        "total_helmets":     len(helmets),
        "helmet_violations": len(heads),
        "violators":         violations,
    }


def _match_via_crops(frame: np.ndarray, heads: list[dict]) -> list[dict]:
   
    violations: list[dict] = []

    for head in heads:
        crop, off_x, off_y = _safe_crop(
            frame,
            head["x1"], head["y1"], head["x2"], head["y2"],
            FACE_CROP_PADDING_PX,
        )

        if crop.size == 0:
            continue

        faces = face_service.get_faces(crop)

        if not faces:
            continue

        # Take the highest-confidence face in the crop (should be exactly one)
        best_face = max(faces, key=lambda f: f.det_score)
        emb = best_face.embedding / np.linalg.norm(best_face.embedding)
        result = face_service.search(emb)

        if result["user_id"] is None:
            continue

        # Translate local crop bbox → full-frame bbox
        lx1, ly1, lx2, ly2 = map(int, best_face.bbox)
        full_box = (
            lx1 + off_x,
            ly1 + off_y,
            lx2 + off_x,
            ly2 + off_y,
        )

        violations.append({
            "user_id":  result["user_id"],
            "name":     result["label"],
            "score":    result["score"],
            "email":    result["email"],
            "face_box": full_box,
        })

    return violations


def _match_via_full_frame(frame: np.ndarray, heads: list[dict]) -> list[dict]:
   
    violations: list[dict] = []
    faces = face_service.get_faces(frame, enhance=True)

    for face in faces:
        fx1, fy1, fx2, fy2 = map(int, face.bbox)
        emb = face.embedding / np.linalg.norm(face.embedding)

        for head in heads:
            head_box = (head["x1"], head["y1"], head["x2"], head["y2"])
            if _face_inside_head((fx1, fy1, fx2, fy2), head_box):
                result = face_service.search(emb)
                if result["user_id"] is not None:
                    violations.append({
                        "user_id":  result["user_id"],
                        "name":     result["label"],
                        "score":    result["score"],
                        "email":    result["email"],
                        "face_box": (fx1, fy1, fx2, fy2),
                    })
                break

    return violations