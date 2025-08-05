from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


class AccountCreate(BaseModel):
    customer_name: str = Field(..., example="Alice Smith")
    account_type: Literal["savings", "current", "fixed"] = Field(..., example="savings")
    initial_deposit: float = Field(..., ge=0, example=500.0)


class AccountResponse(BaseModel):
    account_number: str
    customer_name: str
    account_type: str
    current_balance: float
    created_at: datetime


class TransactionEntry(BaseModel):
    timestamp: datetime
    type: Literal["deposit", "withdrawal"]
    amount: float


class TransactionHistoryResponse(BaseModel):
    account_number: str
    history: List[TransactionEntry]
