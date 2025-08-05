from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

# Load MongoDB URI from environment
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MongoDB URI is missing. Check your .env file.")

# Create a MongoClient instance
client = MongoClient(MONGO_URI)

# Define the database name
db = client["bank_app"]

# Collections that will be used
users_collection = db["users"]
accounts_collection = db["accounts"]
