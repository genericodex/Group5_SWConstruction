from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from domain.transactions import Transaction

@dataclass
class MonthlyStatement:
    account_id: str
    statement_period: str
    start_date: datetime
    end_date: datetime
    starting_balance: float
    ending_balance: float
    interest_earned: float = 0.0
    transactions: List[Transaction] = field(default_factory=list)
    
    @property
    def total_deposits(self) -> float:
        return sum(t.amount for t in self.transactions 
                  if t.transaction_type.name == "DEPOSIT")
    
    @property
    def total_withdrawals(self) -> float:
        return sum(t.amount for t in self.transactions 
                  if t.transaction_type.name == "WITHDRAW")
    
    @property
    def total_transfers_in(self) -> float:
        return sum(t.amount for t in self.transactions 
                  if t.transaction_type.name == "TRANSFER" 
                  and t.destination_account_id == self.account_id)
    
    @property
    def total_transfers_out(self) -> float:
        return sum(t.amount for t in self.transactions 
                  if t.transaction_type.name == "TRANSFER" 
                  and t.source_account_id == self.account_id)
