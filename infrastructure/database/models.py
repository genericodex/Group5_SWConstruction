
from sqlalchemy import Column, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database.db import Base
from domain.accounts import AccountType, AccountStatus
from domain.transactions import TransactionType
from datetime import datetime

class AccountModel(Base):
    __tablename__ = "accounts"

    account_id = Column(String, primary_key=True, index=True)
    account_type = Column(Enum(AccountType), nullable=False)
    balance = Column(Float, default=0.0)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    creation_date = Column(DateTime, default=datetime.now)

    transactions = relationship("TransactionModel", back_populates="account")

class TransactionModel(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    account_id = Column(String, ForeignKey("accounts.account_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    account = relationship("AccountModel", back_populates="transactions")