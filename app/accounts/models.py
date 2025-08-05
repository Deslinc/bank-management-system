from abc import ABC, abstractmethod
from datetime import datetime

class BankAccount(ABC):
    def __init__(self, customer_name, balance=0):
        self.customer_name = customer_name
        self.balance = balance
        self.account_number = id(self)
        self.transaction_history = []

    @abstractmethod
    def withdraw(self, amount):
        pass

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.append(f"[{datetime.now()}] Deposited ${amount}")

    def get_balance(self):
        return self.balance

    def get_transaction_history(self):
        return self.transaction_history

class SavingsAccount(BankAccount):
    MIN_BALANCE = 100

    def withdraw(self, amount):
        if self.balance - amount < self.MIN_BALANCE:
            raise ValueError("Cannot withdraw: minimum balance required.")
        self.balance -= amount
        self.transaction_history.append(f"[{datetime.now()}] Withdrawn ${amount}")

class CurrentAccount(BankAccount):
    OVERDRAFT_LIMIT = -500

    def withdraw(self, amount):
        if self.balance - amount < self.OVERDRAFT_LIMIT:
            raise ValueError("Overdraft limit exceeded.")
        self.balance -= amount
        self.transaction_history.append(f"[{datetime.now()}] Withdrawn ${amount}")

class FixedDepositAccount(BankAccount):
    def __init__(self, customer_name, balance, maturity_date):
        super().__init__(customer_name, balance)
        self.maturity_date = maturity_date

    def withdraw(self, amount):
        if datetime.now() < self.maturity_date:
            raise ValueError("Funds are locked until maturity.")
        self.balance -= amount
        self.transaction_history.append(f"[{datetime.now()}] Withdrawn ${amount}")