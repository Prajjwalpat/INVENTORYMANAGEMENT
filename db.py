from pymongo import MongoClient,errors
from config import MONGO_URI,DB_NAME
from logger import logger

try:
    client=MongoClient(MONGO_URI,serverSelectionTimeoutMS=5000)
    db=client[DB_NAME]
    collection=db["inventory"]
    client.server_info()
    logger.info("Connected to mongodb successfully.")
    collection.create_index("item",unique=True)
except errors.ServerSelectionTimeoutError as e:
    logger.critical(f"Connection failed: {e}")
    collection=None