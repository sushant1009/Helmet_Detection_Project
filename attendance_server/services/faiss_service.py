import faiss
import numpy as np
import threading
from typing import List, Dict, Optional
from database.postgres import get_db_cursor
from database.mongodb import get_embeddings_collection
from config import SIMILARITY_THRESHOLD
from utils.logger import setup_logger



class FaissIndexService:
    def __init__(self):
        self._index_lock = threading.Lock()
        self._worker_id: List[int] = []
        self._supervisor_id: List[int] = []
        self._worker_names: List[str] = []
        self._worker_email: List[str] = []
        self._supervisor_email: List[str] = []
        self._embeddings: List[np.ndarray] = []
        self._faiss_index: Optional[faiss.Index] = None
        self._index_loaded = False
        self._supervisor = None
        self.logger = setup_logger("faiss_service")
        self.logger.info("FAISS Index Service initialized")

    async def load_data_from_db(self, supervisor_id: int) -> Optional[Dict]:
        """Load worker data and embeddings from databases"""
        embeddings = []
        worker_ids = []
        worker_names = []
        worker_emails = []
        supervisor_ids = []
        supervisor_emails = []
        global super
        
        try:
            # PostgreSQL query
            with get_db_cursor() as cursor:
                query = """
                SELECT w.worker_id, w.full_name, w.email, w.supervisor_id, s.email
                FROM workers w JOIN supervisor s
                ON w.supervisor_id = s.supervisor_id
                WHERE w.supervisor_id = %s;
                """
                cursor.execute(query, (supervisor_id,))
                rows = cursor.fetchall()
                self.logger.info(f"Fetched {len(rows)} workers for supervisor_id: {supervisor_id}")
            # MongoDB query
            embeddings_col = get_embeddings_collection()
            embedding_docs = list(embeddings_col.find(
                {"supervisorId": int(supervisor_id)},
                {"workerId": 1, "embeddings": 1, "_id": 0}
            ))
            self.logger.info(f"Fetched {len(embedding_docs)} embedding documents for supervisor_id: {supervisor_id}")
            embeddings_dict = {doc["workerId"]: doc["embeddings"] for doc in embedding_docs}
            
            # Match workers with embeddings
            for row in rows:
                worker_id = int(row[0])
                
                if worker_id in embeddings_dict:
                    embeddings.append(embeddings_dict[worker_id])
                    worker_ids.append(row[0])
                    worker_names.append(row[1])
                    worker_emails.append(row[2])
                    supervisor_ids.append(row[3])
                    supervisor_emails.append(row[4])
                else:
                    self.logger.warning(f"No embedding found for worker_id: {worker_id}")
            
            return {
                "embeddings": embeddings,
                "worker_ids": worker_ids,
                "worker_names": worker_names,
                "worker_emails": worker_emails,
                "supervisor_ids": supervisor_ids,
                "supervisor_emails": supervisor_emails
            }
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return None

    def build_faiss_index(self, embeddings_list: List[np.ndarray]) -> faiss.Index:
        """Build FAISS index from embeddings"""
        if len(embeddings_list) == 0:
            self.logger.error("No embeddings found to build FAISS index")
            raise ValueError("No embeddings found to build FAISS index")

        vectors = np.array(embeddings_list).astype("float32")
        faiss.normalize_L2(vectors)

        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)

        self.logger.info(f"FAISS index loaded with {index.ntotal} vectors")
        return index

    async def initialize_index(self, supervisor_id: int):
        """Initialize FAISS index for a supervisor"""
        data = await self.load_data_from_db(supervisor_id)
        
        if not data or len(data["embeddings"]) == 0:
            self.logger.warning(f"No data found for supervisor_id: {supervisor_id}")
            raise ValueError("No data found for supervisor")
        
        self._embeddings = data["embeddings"]
        self._worker_id = data["worker_ids"]
        self._worker_names = data["worker_names"]
        self._worker_email = data["worker_emails"]
        self._supervisor_id = data["supervisor_ids"]
        self._supervisor_email = data["supervisor_emails"]
        
        self._faiss_index = self.build_faiss_index(self._embeddings)
        self._index_loaded = True
        self._supervisor = supervisor_id

    async def reload_index(self):
        """Reload FAISS index with current supervisor data"""
        if self._supervisor is None:
            self.logger.error("No supervisor set for reloading index")
            raise ValueError("No supervisor set")
        
        # Clear old data
        self._embeddings.clear()
        self._worker_id.clear()
        self._worker_names.clear()
        self._worker_email.clear()
        self._supervisor_id.clear()
        self._supervisor_email.clear()
        self.logger.info("Cleared old FAISS index data")
        
        # Reload
        await self.initialize_index(self._supervisor)
        self.logger.info("FAISS index reloaded successfully")
        

    def search_embedding(self, emb: np.ndarray, bbox: np.ndarray) -> dict:
        """Search for face embedding in FAISS index"""
        if self._faiss_index is None:
            return {
                "label": "Unknown",
                "user_id": None,
                "score": 0.0,
                "x1": int(bbox[0]), "y1": int(bbox[1]),
                "x2": int(bbox[2]), "y2": int(bbox[3])
            }
        
        query = emb.reshape(1, -1).astype("float32")
        faiss.normalize_L2(query)

        with self._index_lock:
            D, I = self._faiss_index.search(query, 1)
            score = float(D[0][0])
            idx = int(I[0][0])
            
            
            label = "Unknown"
            user_id = None
            if 0 <= idx < len(self._worker_id):
                if score >= SIMILARITY_THRESHOLD:
                    label = self._worker_names[idx]
                    user_id = self._worker_id[idx]

        return {
            "label": label,
            "user_id": user_id,
            "score": score,
            "x1": int(bbox[0]), "y1": int(bbox[1]),
            "x2": int(bbox[2]), "y2": int(bbox[3])
        }

    @property
    def is_loaded(self) -> bool:
        return self._index_loaded

# Global instance
faiss_service = FaissIndexService()