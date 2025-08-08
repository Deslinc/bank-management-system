from fastapi import APIRouter, HTTPException, Depends
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel
from app.core.database import accounts_collection
from app.accounts.logic import create_account
from app.auth.utils import get_current_token_data
from app.auth.schemas import TokenData

router = APIRouter(tags=["Accounts"])

class AccountCreateReq(BaseModel):
    initial_balance: float
    account_type: str  # "SAVINGS", "CURRENT", "FIXED DEPOSIT"

class TransactionReq(BaseModel):
    account_id: str
    amount: float

@router.post("/create")
def create_new_account(
    data: AccountCreateReq,
    token_data: TokenData = Depends(get_current_token_data)
):
    owner_email = token_data.email
    owner_username = token_data.username
    account_type = data.account_type.lower()

    # ✅ Check if user already has this account type
    existing_account = accounts_collection.find_one({
        "owner_email": owner_email,
        "type": account_type
    })
    if existing_account:
        raise HTTPException(
            status_code=400,
            detail=f"You already have a {data.account_type} account."
        )

    # Create account object using your OOP logic
    acc_obj = create_account(data.account_type, owner_username, data.initial_balance)

    # Save to DB
    acc_doc = {
        "owner_email": owner_email,
        "owner_username": owner_username,
        "balance": acc_obj.get_balance(),
        "type": account_type,  
        "transactions": acc_obj.get_transaction_history(),
        "created_at": datetime.now()
    }
    result = accounts_collection.insert_one(acc_doc)
    return {"account_id": str(result.inserted_id)}

@router.post("/deposit")
def deposit_funds(
    tx: TransactionReq,
    token_data: TokenData = Depends(get_current_token_data)
):
    acc = accounts_collection.find_one({"_id": ObjectId(tx.account_id)})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if acc.get("owner_email") != token_data.email:
        raise HTTPException(status_code=403, detail="Forbidden: not your account")

    new_balance = acc["balance"] + tx.amount
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    acc.setdefault("transactions", []).append(f"[{timestamp}] Deposited ${tx.amount}")
    accounts_collection.update_one(
        {"_id": ObjectId(tx.account_id)},
        {"$set": {"balance": new_balance, "transactions": acc["transactions"]}}
    )
    return {"message": "Deposit successful", "balance": new_balance}

@router.post("/withdraw")
def withdraw_funds(
    tx: TransactionReq,
    token_data: TokenData = Depends(get_current_token_data)
):
    acc = accounts_collection.find_one({"_id": ObjectId(tx.account_id)})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if acc.get("owner_email") != token_data.email:
        raise HTTPException(status_code=403, detail="Forbidden: not your account")

    new_balance = acc["balance"] - tx.amount
    account_type = acc.get("type", "").upper()

    if account_type == "SAVINGS" and new_balance < 100:
        raise HTTPException(status_code=400, detail="Cannot go below $100 for savings account")
    elif account_type == "CURRENT" and new_balance < -500:
        raise HTTPException(status_code=400, detail="Overdraft limit exceeded for current account")
    elif account_type == "FIXED DEPOSIT":
        raise HTTPException(status_code=400, detail="Withdrawals not allowed for fixed deposit account")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    acc.setdefault("transactions", []).append(f"[{timestamp}] Withdrawn ${tx.amount}")
    accounts_collection.update_one(
        {"_id": ObjectId(tx.account_id)},
        {"$set": {"balance": new_balance, "transactions": acc["transactions"]}}
    )
    return {"message": "Withdrawal successful", "balance": new_balance}

@router.get("/balance/{account_id}")
def get_balance(
    account_id: str,
    token_data: TokenData = Depends(get_current_token_data)
):
    acc = accounts_collection.find_one({"_id": ObjectId(account_id)})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if acc.get("owner_email") != token_data.email:
        raise HTTPException(status_code=403, detail="Forbidden: not your account")
    return {"balance": acc["balance"]}

@router.get("/transactions/{account_id}")
def get_transaction_history(
    account_id: str,
    token_data: TokenData = Depends(get_current_token_data)
):
    acc = accounts_collection.find_one({"_id": ObjectId(account_id)})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if acc.get("owner_email") != token_data.email:
        raise HTTPException(status_code=403, detail="Forbidden: not your account")
    return {"transactions": acc.get("transactions", [])}
