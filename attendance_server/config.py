import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL Configuration
PG_HOST = os.getenv("PG_HOST")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USERNAME = os.getenv("PG_USERNAME")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_PORT = os.getenv("PG_PORT")
DIRECT_URL = os.getenv("DIRECT_URL")

# MongoDB Configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_APP = os.getenv("DB_APP")
DB_NAME = os.getenv("DB_NAME")
MONGO_URI = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{DB_APP}.iilebsg.mongodb.net/{DB_NAME}?retryWrites=true&w=majority&appName={DB_APP}"

# Application Settings
SIMILARITY_THRESHOLD = float(os.getenv("FACE_SIMILARITY_THRESHOLD"))
ATTENDANCE_URL = os.getenv("ATTENDANCE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Queue Settings
FRAME_QUEUE_MAXSIZE = 10