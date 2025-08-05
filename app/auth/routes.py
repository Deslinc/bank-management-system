from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from pymongo.collection import Collection
from app.auth.utils import create_access_token
from app.auth.schemas import UserCreate, UserInDB
from app.core.database import users_collection
from pydantic import BaseModel

router = APIRouter(tags=["Authentication"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

# -----------------------------
# Helper Functions
# -----------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_username(username: str, collection: Collection):
    user_data = collection.find_one({"username": username})
    if user_data:
        return UserInDB(**user_data)
    return None


# -----------------------------
# Register New User
# -----------------------------
@router.post("/signup")
def signup(user: UserCreate):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pwd = hash_password(user.password)
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hashed_pwd
    del user_dict["password"]  # Remove plaintext password

    result = users_collection.insert_one(user_dict)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {"message": "User registered successfully"}



# -----------------------------
# Login and Get JWT
# -----------------------------
@router.post("/login")
def login(credentials: LoginRequest):
    user = get_user_by_username(credentials.username, users_collection)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
