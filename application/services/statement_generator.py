from abc import ABC, abstractmethod
from typing import Dict


class IStatementGenerator(ABC):
    @abstractmethod
    def generate_pdf(self, statement_data: Dict) -> str:
        pass

    @abstractmethod
    def generate_csv(self, statement_data: Dict) -> str:
        pass