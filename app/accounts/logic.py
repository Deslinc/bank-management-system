from datetime import datetime, timedelta
from app.accounts.models import SavingsAccount, CurrentAccount, FixedDepositAccount

def create_account(account_type, name, initial_balance, maturity_days=30):
    # Normalize type
    # account_type = account_type.strip().upper()

    if account_type == "SAVINGS":
        return SavingsAccount(name, initial_balance)
    elif account_type == "CURRENT":
        return CurrentAccount(name, initial_balance)
    elif account_type == "FIXED DEPOSIT":
        maturity = datetime.now() + timedelta(days=maturity_days)
        return FixedDepositAccount(name, initial_balance, maturity)
    else:
        raise ValueError("Invalid account type")
