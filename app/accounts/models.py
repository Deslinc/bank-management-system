from datetime import datetime, timedelta

class BankAccount:
    def __init__(self, owner, balance=0.0):
        self.owner = owner
        self.balance = balance
        self.transactions = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.transactions.append(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Deposited ${amount}"
        )

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.transactions.append(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Withdrawn ${amount}"
        )

    def get_balance(self):
        return self.balance

    def get_transaction_history(self):
        return self.transactions


class SavingsAccount(BankAccount):
    MIN_BALANCE = 100

    def __init__(self, owner, balance=0.0):
        if balance < self.MIN_BALANCE:
            raise ValueError(f"Minimum balance for savings account is ${self.MIN_BALANCE}")
        super().__init__(owner, balance)

    def withdraw(self, amount):
        if self.balance - amount < self.MIN_BALANCE:
            raise ValueError("Cannot withdraw: balance would drop below $100 minimum")
        super().withdraw(amount)


class CurrentAccount(BankAccount):
    OVERDRAFT_LIMIT = -500

    def withdraw(self, amount):
        if self.balance - amount < self.OVERDRAFT_LIMIT:
            raise ValueError("Overdraft limit exceeded")
        super().withdraw(amount)


class FixedDepositAccount(BankAccount):
    def __init__(self, owner, balance=0.0, duration_months=6):
        if balance <= 0:
            raise ValueError("Initial deposit must be positive for fixed deposit account")
        super().__init__(owner, balance)
        self.maturity_date = datetime.now() + timedelta(days=30 * duration_months)
        self.initial_deposit_done = True  # no more deposits allowed after creation

    def deposit(self, amount):
        raise ValueError("Cannot deposit into a fixed deposit account after creation")

    def withdraw(self, amount):
        if datetime.now() < self.maturity_date:
            raise ValueError("Cannot withdraw before maturity date")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        super().withdraw(amount)
