from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., example="deslinc")
    password: str = Field(..., min_length=6, example="strong_password")


class UserInDB(BaseModel):
    username: str
    hashed_password: str


class UserLogin(BaseModel):
    username: str = Field(..., example="deslinc")
    password: str = Field(..., min_length=6, example="strong_password")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# For decoding and verifying JWT token payloads
class TokenData(BaseModel):
    username: str | None = None
