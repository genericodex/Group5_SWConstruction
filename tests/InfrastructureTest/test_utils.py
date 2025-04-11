from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database.db import Base
from domain.accounts import AccountType, AccountStatus
from domain.transactions import TransactionType

# Create an in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_database():
    # Create all tables in the in-memory database
    Base.metadata.create_all(bind=engine)

def get_test_session():
    # Create a new session for testing
    session = SessionLocal()
    return session

def teardown_database():
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)