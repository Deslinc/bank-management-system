from pymongo import MongoClient
from app.core.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["mybankdb"]

users_collection = db["users"]
accounts_collection = db["accounts"]

# Optional: Ensure indexes for performance & uniqueness
users_collection.create_index("email", unique=True)
users_collection.create_index("username", unique=True)
