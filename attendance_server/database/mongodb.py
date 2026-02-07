from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# Initialize MongoDB connection pool
mongo_client = MongoClient(
    MONGO_URI,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000
)

mongo_db = mongo_client[DB_NAME]

def get_embeddings_collection():
    """Get embeddings collection"""
    return mongo_db["embeddings"]

def close_mongo_client():
    """Close MongoDB connection"""
    if mongo_client:
        mongo_client.close()
        print("MongoDB client closed")