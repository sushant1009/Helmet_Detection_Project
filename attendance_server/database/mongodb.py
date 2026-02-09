from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from utils.logger import setup_logger

logger = setup_logger("database.mongodb")
logger.info("Initializing MongoDB client")
mongo_client = MongoClient(
    MONGO_URI,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000
)
logger.info("MongoDB client initialized successfully")
mongo_db = mongo_client[DB_NAME]
logger.info(f"Connected to MongoDB database: {DB_NAME}")
def get_embeddings_collection():
    """Get embeddings collection"""
    return mongo_db["embeddings"]

def close_mongo_client():
    """Close MongoDB connection"""
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB client closed")