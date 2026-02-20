import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


# ── Auth ──────────────────────────────────────────────────────────────────────
SECRET_KEY: str = os.environ["SECRET_KEY"]
ALGORITHM: str = os.environ["ALGORITHM"]

# ── Detection / similarity ────────────────────────────────────────────────────
DETECTION_CONFIDENCE: float = float(os.getenv("DETECTION_CONFIDENCE", "0.35"))
EMBED_DIM: int = int(os.getenv("EMBED_DIM", "512"))
SIMILARITY_THRESHOLD: float = float(os.environ["FACE_SIMILARITY_THRESHOLD"])

# ── Violation throttle ────────────────────────────────────────────────────────
VIOLATION_THRESHOLD: timedelta = timedelta(
    minutes=int(os.environ["VIOLATION_THRESHOLD"])
)

MAX_VIOLATIONS_BEFORE_SUPERVISOR_ALERT: int = int(
    os.getenv("MAX_VIOLATIONS_BEFORE_SUPERVISOR_ALERT", "5")
)
MIN_FRAMES_BETWEEN_VIOLATIONS = int(os.getenv("MIN_FRAMES_BETWEEN_VIOLATIONS", "5"))  # BUG FIX: new config for eviction grace frames    

YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH")

# ── Face recognition — crop mode ─────────────────────────────────────────────
# When True (default), InsightFace runs on a tight crop of each no_helmet
# bounding box instead of the full frame. Much faster when there are few
# violations in a large scene; slightly slower only if the entire frame
# is filled with faces (rare in site/warehouse environments).
FACE_CROP_MODE: bool = os.getenv("FACE_CROP_MODE", "true").lower() == "true"

# Padding (pixels) added around a no_helmet box before cropping and passing
# to InsightFace. Gives the face detector enough context to find the face
# even if it extends slightly outside the YOLO bounding box.
FACE_CROP_PADDING_PX: int = int(os.getenv("FACE_CROP_PADDING_PX", "20"))

# ── External service ──────────────────────────────────────────────────────────
VIOLATION_URL: str = os.environ["VIOLATION_URL"]

# ── Databases ─────────────────────────────────────────────────────────────────
PG_DSN: dict = {
    "host": os.environ["PG_HOST"],
    "database": os.environ["PG_DATABASE"],
    "user": os.environ["PG_USERNAME"],
    "password": os.environ["PG_PASSWORD"],
    "port": int(os.getenv("PG_PORT", "5432")),
    "sslmode": "require",
}
DIRECT_URL: str = os.getenv("DIRECT_URL")

_DB_USER = os.environ["DB_USER"]
_DB_PASSWORD = os.environ["DB_PASSWORD"]
_DB_APP = os.environ["DB_APP"]
_DB_NAME = os.environ["DB_NAME"]
MONGO_URI: str = (
    f"mongodb+srv://{_DB_USER}:{_DB_PASSWORD}"
    f"@{_DB_APP}.iilebsg.mongodb.net/{_DB_NAME}"
    f"?retryWrites=true&w=majority&appName={_DB_APP}"
)
MONGO_DB_NAME: str = _DB_NAME

# ── WebSocket / frame queue ───────────────────────────────────────────────────
FRAME_QUEUE_SIZE: int = int(os.getenv("FRAME_QUEUE_SIZE", "7"))
INSIGHTFACE_DET_SIZE: tuple[int, int] = (640, 640)

#Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CLEAR_LOGS_ON_STARTUP = os.getenv("CLEAR_LOGS_ON_STARTUP", "true").lower() == "true"
