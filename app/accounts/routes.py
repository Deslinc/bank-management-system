from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from bson import ObjectId

from app.core.database import accounts_collection
from app.accounts.models import SavingsAccount, CurrentAccount, FixedDepositAccount
from app.auth.utils import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


# Create Account
@router.post("/create")
def create_account(account_type: str, initial_deposit: float, current_user: dict = Depends(get_current_user)):
    # Check if user already has this account type
    existing = accounts_collection.find_one({"owner_id": current_user["_id"], "account_type": account_type})
    if existing:
        raise HTTPException(status_code=400, detail=f"You already have a {account_type} account")

    # Create account based on type and rules
    if account_type.upper() == "SAVINGS":
        try:
            account = SavingsAccount(owner=current_user["_id"], balance=initial_deposit)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    elif account_type.lower() == "current":
        account = CurrentAccount(owner=current_user["_id"], balance=initial_deposit)

    elif account_type.lower() == "fixed":
        try:
            account = FixedDepositAccount(owner=current_user["_id"], balance=initial_deposit, duration_months=6)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    else:
        raise HTTPException(status_code=400, detail="Invalid account type")

    # Save to DB
    account_doc = {
        "owner_id": current_user["_id"],
        "account_type": account_type.lower(),
        "balance": account.balance,
        "transactions": account.transactions,
        "maturity_date": getattr(account, "maturity_date", None),
        "created_at": datetime.now()
    }
    result = accounts_collection.insert_one(account_doc)

    return {
        "message": f"{account_type.capitalize()} account created successfully",
        "account_id": str(result.inserted_id)  # Return the MongoDB assigned account ID
    }


# Deposit
@router.post("/{account_id}/deposit")
def deposit(account_id: str, amount: float, current_user: dict = Depends(get_current_user)):
    account = accounts_collection.find_one({"_id": ObjectId(account_id), "owner_id": current_user["_id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Restrict deposits for fixed deposit accounts
    if account["account_type"] == "fixed":
        raise HTTPException(status_code=400, detail="Cannot deposit into fixed deposit account after creation")

    # Update using model logic
    if account["account_type"] == "savings":
        acc_obj = SavingsAccount(owner=account["owner_id"], balance=account["balance"])
    elif account["account_type"] == "current":
        acc_obj = CurrentAccount(owner=account["owner_id"], balance=account["balance"])
    else:
        raise HTTPException(status_code=400, detail="Unsupported account type for deposit")

    try:
        acc_obj.deposit(amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save updated balance and transactions
    accounts_collection.update_one(
        {"_id": ObjectId(account_id)},
        {"$set": {"balance": acc_obj.balance, "transactions": acc_obj.transactions}}
    )
    return {"message": "Deposit successful"}


# Withdraw
@router.post("/{account_id}/withdraw")
def withdraw(account_id: str, amount: float, current_user: dict = Depends(get_current_user)):
    account = accounts_collection.find_one({"_id": ObjectId(account_id), "owner_id": current_user["_id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Create account object based on type
    if account["account_type"] == "savings":
        acc_obj = SavingsAccount(owner=account["owner_id"], balance=account["balance"])
    elif account["account_type"] == "current":
        acc_obj = CurrentAccount(owner=account["owner_id"], balance=account["balance"])
    elif account["account_type"] == "fixed":
        acc_obj = FixedDepositAccount(owner=account["owner_id"], balance=account["balance"])
        acc_obj.maturity_date = account["maturity_date"]

        # Check maturity date
        if datetime.now() < acc_obj.maturity_date:
            raise HTTPException(status_code=400, detail="Cannot withdraw before maturity date")
    else:
        raise HTTPException(status_code=400, detail="Invalid account type")

    try:
        acc_obj.withdraw(amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save updated balance and transactions
    accounts_collection.update_one(
        {"_id": ObjectId(account_id)},
        {"$set": {"balance": acc_obj.balance, "transactions": acc_obj.transactions}}
    )
    return {"message": "Withdrawal successful"}

# Get Account Balance
@router.get("/{account_id}/balance")
def get_balance(account_id: str, current_user: dict = Depends(get_current_user)):
    account = accounts_collection.find_one({"_id": ObjectId(account_id), "owner_id": current_user["_id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"balance": account["balance"]}

# Get Transaction History
@router.get("/{account_id}/transactions")
def get_transactions(account_id: str, current_user: dict = Depends(get_current_user)):
    account = accounts_collection.find_one({"_id": ObjectId(account_id), "owner_id": current_user["_id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"transactions": account["transactions"]}
