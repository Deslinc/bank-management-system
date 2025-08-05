# app/auth/logic.py

from app.auth.schemas import UserCreate, UserInDB

# In-memory fake users database (temporary until MongoDB is connected)
fake_users_db = {}

def fake_hash_password(password: str):
    return "hashed_" + password

async def create_user(user: UserCreate):
    if user.username in fake_users_db:
        raise ValueError("User already exists")

    hashed_password = fake_hash_password(user.password)
    user_in_db = UserInDB(
        username=user.username,
        password=user.password,
        hashed_password=hashed_password
    )

    # Simulate storing user (avoid storing plaintext password in real apps)
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hashed_password
    }

    return user_in_db

async def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return None

    hashed_password = fake_hash_password(password)
    if hashed_password != user["hashed_password"]:
        return None

    return UserInDB(
        username=username,
        password=password,
        hashed_password=hashed_password
    )
