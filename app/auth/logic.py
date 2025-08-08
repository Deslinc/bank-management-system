# app/auth/logic.py

from app.auth.schemas import UserCreate, UserInDB
from app.core.database import db
from app.auth.utils import get_password_hash, verify_password

async def create_user(user: UserCreate):
    # Check if email is already registered
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise ValueError("A user with this email already exists")

    hashed_password = get_password_hash(user.password)

    user_data = {
        "username": user.username,  # can be non-unique
        "email": user.email,        # must be unique
        "hashed_password": hashed_password
    }

    result = await db["users"].insert_one(user_data)

    return UserInDB(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        password=user.password  # not stored in DB, just for schema return
    )

async def authenticate_user(email: str, password: str):
    # Find user by email
    user = await db["users"].find_one({"email": email})
    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return UserInDB(
        username=user["username"],
        email=user["email"],
        hashed_password=user["hashed_password"],
        password=password  # for schema
    )
