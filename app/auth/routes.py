# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.auth.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.auth.utils import hash_password, verify_password, create_access_token, get_current_token_data
from app.core.database import users_collection  # direct collection import

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )

    hashed_pw = hash_password(user.password)
    user_dict = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pw
    }
    result = users_collection.insert_one(user_dict)

    return UserResponse(
        id=str(result.inserted_id),
        username=user.username,
        email=user.email
    )

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    user = users_collection.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": user["username"], "email": user["email"]})
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserResponse)
def get_me(token_data = Depends(get_current_token_data)):
    user = users_collection.find_one({"email": token_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"]
    )
