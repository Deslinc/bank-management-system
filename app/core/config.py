import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Fail fast if critical env vars are missing
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI is not set in environment variables")
if not JWT_SECRET_KEY:
    raise ValueError("❌ JWT_SECRET_KEY is not set in environment variables")
