from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId
from app.core.database import accounts_collection
from app.accounts.logic import create_account
from pydantic import BaseModel
from datetime import datetime

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
    acc = accounts_collection.find_one({"_id": ObjectId(tx.account_id)})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    new_balance = acc["balance"] + tx.amount
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    acc["transactions"].append(f"[{timestamp}] Deposited ${tx.amount}")
    accounts_collection.update_one(
        {"_id": ObjectId(tx.account_id)},
        {"$set": {"balance": new_balance, "transactions": acc["transactions"]}}
    )
    return {"message": "Deposit successful"}

@router.post("/withdraw")
def withdraw_funds(tx: Transaction):
    acc = accounts_collection.find_one({"_id": ObjectId(tx.account_id)})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    new_balance = acc["balance"] - tx.amount
    account_type = acc.get("type")
    
    # Apply rules based on account type
    if account_type == "savings" and new_balance < 100:
        raise HTTPException(status_code=400, detail="Cannot go below $100 for savings account")
    elif account_type == "current" and new_balance < -500:
        raise HTTPException(status_code=400, detail="Overdraft limit exceeded for current account")
    elif account_type == "fixed":
        raise HTTPException(status_code=400, detail="Withdrawals not allowed for fixed deposit account")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    acc["transactions"].append(f"[{timestamp}] Withdrawn ${tx.amount}")
    accounts_collection.update_one(
        {"_id": ObjectId(tx.account_id)},
        {"$set": {"balance": new_balance, "transactions": acc["transactions"]}}
    )
    return {"message": "Withdrawal successful"}

@router.get("/balance/{account_id}")
def get_balance(account_id: str):
    acc = accounts_collection.find_one({"_id": ObjectId(account_id)})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"balance": acc["balance"]}

@router.get("/transactions/{account_id}")
def get_transaction_history(account_id: str):
    acc = accounts_collection.find_one({"_id": ObjectId(account_id)})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"transactions": acc.get("transactions", [])}
