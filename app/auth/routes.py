from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pymongo.collection import Collection
from bson.objectid import ObjectId

from app.auth.utils import create_access_token
from app.auth.schemas import UserCreate, UserInDB
from app.core.database import users_collection

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


# -----------------------------
# Register New User
# -----------------------------
@router.post("/signup")
def signup(user: UserCreate):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pwd = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_pwd

    result = users_collection.insert_one(user_dict)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {"message": "User registered successfully"}



# -----------------------------
# Login and Get JWT
# -----------------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username, users_collection)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
