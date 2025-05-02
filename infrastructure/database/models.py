from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database.db import Base
from datetime import datetime

class AccountModel(Base):
    __tablename__ = "accounts"

    account_id = Column(String, primary_key=True, index=True)
    account_type = Column(String, nullable=False)  # Store the name property as string
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    status = Column(String, default="ACTIVE")  # Store the name property as string
    creation_date = Column(DateTime, default=datetime.now)

    transactions = relationship("TransactionModel", back_populates="account")

class TransactionModel(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    transaction_type = Column(String, nullable=False)  # Store the name property as string
    amount = Column(Float, nullable=False)
    account_id = Column(String, ForeignKey("accounts.account_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    # Added fields for transfer transactions
    source_account_id = Column(String, nullable=True)
    destination_account_id = Column(String, nullable=True)

    account = relationship("AccountModel", back_populates="transactions")