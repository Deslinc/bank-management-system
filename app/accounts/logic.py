from datetime import datetime, timedelta
from app.accounts.models import SavingsAccount, CurrentAccount, FixedDepositAccount

def create_account(account_type, name, initial_balance):
    if account_type == "savings":
        return SavingsAccount(name, initial_balance)
    elif account_type == "current":
        return CurrentAccount(name, initial_balance)
    elif account_type == "fixed":
        maturity = datetime.now() + timedelta(days=30)  # simulate 30-day lock
        return FixedDepositAccount(name, initial_balance, maturity)
    else:
        raise ValueError("Invalid account type")