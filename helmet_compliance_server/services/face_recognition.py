"""
Face recognition service.

Owns the InsightFace model, the FAISS index, and all worker identity data.
One global singleton is shared across all camera sessions.
"""
from __future__ import annotations

import threading
import numpy as np
import faiss
import insightface
import psycopg2
from pymongo import MongoClient
from database.postgres import get_db_cursor
from database.mongodb import get_embeddings_collection, close_mongo_client
from utils.logger import setup_logger

from config import (
    EMBED_DIM,
    SIMILARITY_THRESHOLD,
    PG_DSN,
    MONGO_URI,
    MONGO_DB_NAME,
    INSIGHTFACE_DET_SIZE,
)

logger = setup_logger("services.face_recognition")

class FaceRecognitionService:
    """Thread-safe face recognition backed by a FAISS flat inner-product index."""

    def __init__(
        self
    ) -> None:
        self._lock = threading.RLock()

        # Per-worker metadata (parallel lists, same ordering as FAISS vectors)
        self._worker_ids: list[int] = []
        self._worker_names: list[str] = []
        self._worker_emails: list[str] = []

        self._faiss_index: faiss.Index | None = None
        self._index_loaded = False

        

        # InsightFace — CPU only; swap provider for GPU deployments
        self._face_model = insightface.app.FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )
        self._face_model.prepare(ctx_id=-1, det_size=INSIGHTFACE_DET_SIZE)
        logger.info("[FaceRecognitionService] InsightFace model loaded.")

    # ── Public helpers ────────────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        with self._lock:
            return self._index_loaded

    def get_faces(self, frame: np.ndarray):
        return self._face_model.get(frame)

    def search(self, embedding: np.ndarray) -> dict:
        
        with self._lock:
            if self._faiss_index is None:
                return {"label": "Unknown", "user_id": None, "score": 0.0}

            query = embedding.reshape(1, -1).astype("float32")
            faiss.normalize_L2(query)
            distances, indices = self._faiss_index.search(query, 1)

            score = float(distances[0][0])
            idx = int(indices[0][0])
            if idx < 0 or score < SIMILARITY_THRESHOLD:
                return {"label": "Unknown", "user_id": None, "score": score}
            
            return {
                "label": self._worker_names[idx],
                "user_id": self._worker_ids[idx],
                "email": self._worker_emails[idx],
                "score": score,
            }

    def reload_for_supervisor(self, supervisor_id: int) -> int:
        """
        Reload all worker embeddings for the given supervisor and rebuild
        the FAISS index.  Returns the number of workers loaded.
        Raises ValueError if no embeddings are found.
        """
        worker_ids, worker_names, worker_emails, raw_embeddings = (
            self._fetch_from_db(supervisor_id)
        )

        if not raw_embeddings:
            raise ValueError(
                f"No embeddings found for supervisor_id={supervisor_id}"
            )

        index = self._build_index(raw_embeddings)

        with self._lock:
            self._worker_ids = worker_ids
            self._worker_names = worker_names
            self._worker_emails = worker_emails
            self._faiss_index = index
            self._index_loaded = True

        logger.info(
            f"[FaceRecognitionService] Index rebuilt with {index.ntotal} vectors"
            f" for supervisor_id={supervisor_id}."
        )
        return index.ntotal

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _fetch_from_db(
        supervisor_id: int,
    ) -> tuple[list, list, list, list]:
        """Pull worker rows from Postgres and embeddings from MongoDB."""
        worker_ids, worker_names, worker_emails, raw_embeddings = [], [], [], []

       
        mongo_client = MongoClient(MONGO_URI)
        try:
            embeddings_col = get_embeddings_collection()

            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT worker_id, full_name, email, supervisor_id
                    FROM workers
                    WHERE supervisor_id = %s;
                    """,
                    (supervisor_id,),
                )
                rows = cursor.fetchall()

            for w_id, full_name, email, sup_id in rows:
                doc = embeddings_col.find_one(
                    {"workerId": int(w_id), "supervisorId": int(sup_id)},
                    {"embeddings": 1, "_id": 0},
                )
                if doc:
                    raw_embeddings.append(doc["embeddings"])
                    worker_ids.append(w_id)
                    worker_names.append(full_name)
                    worker_emails.append(email)
                else:
                    logger.warning(
                        f"[FaceRecognitionService] No embedding found for"
                        f" worker_id={w_id}"
                    )
        except Exception as exc:
            logger.error(f"[FaceRecognitionService] DB error: {exc}")
           

        return worker_ids, worker_names, worker_emails, raw_embeddings

    @staticmethod
    def _build_index(embeddings_list: list) -> faiss.Index:
        vectors = np.array(embeddings_list, dtype="float32")
        faiss.normalize_L2(vectors)
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        return index



face_service = FaceRecognitionService()