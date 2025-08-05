from fastapi import APIRouter, HTTPException
from app.core.database import accounts_collection
from app.accounts.logic import create_account
from pydantic import BaseModel

router = APIRouter()

class AccountCreate(BaseModel):
    name: str
    initial_balance: float
    type: str  # savings, current, fixed

class Transaction(BaseModel):
    account_id: str
    amount: float

@router.post("/create")
def create_new_account(data: AccountCreate):
    try:
        acc = create_account(data.type, data.name, data.initial_balance)
        acc_data = {
            "name": acc.customer_name,
            "balance": acc.get_balance(),
            "type": data.type,
            "transactions": acc.get_transaction_history(),
        }
        result = accounts_collection.insert_one(acc_data)
        return {"account_id": str(result.inserted_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deposit")
def deposit_funds(tx: Transaction):
    acc = accounts_collection.find_one({"_id": tx.account_id})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    new_balance = acc["balance"] + tx.amount
    acc["transactions"].append(f"Deposited ${tx.amount}")
    accounts_collection.update_one({"_id": tx.account_id}, {"$set": {"balance": new_balance, "transactions": acc["transactions"]}})
    return {"message": "Deposit successful"}
