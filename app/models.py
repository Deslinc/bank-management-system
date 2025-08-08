# app/models.py
from passlib.context import CryptContext
from bson import ObjectId
from datetime import datetime
from app.core.database import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users_collection = db["users"]

class User:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def create_user(email: str, username: str, password: str):
        user_data = {
            "_id": str(ObjectId()),
            "email": email,
            "username": username,
            "password": User.hash_password(password),  # keep as "password" to match routes
            "created_at": datetime.utcnow()
        }
        await users_collection.insert_one(user_data)
        return user_data

    @staticmethod
    async def find_by_email(email: str):
        return await users_collection.find_one({"email": email})

    @staticmethod
    async def find_by_username(username: str):
        return await users_collection.find_one({"username": username})
