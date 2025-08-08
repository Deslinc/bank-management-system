from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., example="Desmond Me")
    email: EmailStr = Field(..., example="mymail@example.com")
    password: str = Field(..., min_length=6, example="strong_password")

class UserInDB(UserCreate):
    hashed_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, example="strong_password")

class TokenResponse(BaseModel):  
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
