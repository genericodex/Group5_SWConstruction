from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Optional, Any


class InterestDataSource(ABC):
    """Abstract interface for interest data sources"""

    @abstractmethod
    def get(self, account_type: str) -> Optional[float]:
        """Get interest rate for a specific account type"""
        pass

    @abstractmethod
    def set(self, account_type: str, rate: float) -> None:
        """Set interest rate for a specific account type"""
        pass


class FileInterestDataSource(InterestDataSource):
    """Implementation of interest data source using a JSON file"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Creates the file with default data if it doesn't exist"""
        if not os.path.exists(self.file_path):
            default_rates = {
                "savings": 0.025,  # 2.5%
                "checking": 0.001  # 0.1%
            }
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            with open(self.file_path, 'w') as file:
                json.dump(default_rates, file)

    def _read_data(self) -> Dict[str, float]:
        """Read data from the file"""
        for attempt in range(2):  # Try at most twice
            try:
                with open(self.file_path, 'r') as file:
                    return json.load(file)
            except FileNotFoundError:
                self._ensure_file_exists()
            except json.JSONDecodeError:
                if os.path.exists(self.file_path):
                    os.remove(self.file_path)
                self._ensure_file_exists()
        raise ValueError("Unable to read interest rate data after retry")

    def _write_data(self, data: Dict[str, float]) -> None:
        """Write data to the file"""
        with open(self.file_path, 'w') as file:
            json.dump(data, file)

    def get(self, account_type: str) -> Optional[float]:
        """Get interest rate for a specific account type"""
        data = self._read_data()
        return data.get(account_type)

    def set(self, account_type: str, rate: float) -> None:
        """Set interest rate for a specific account type"""
        data = self._read_data()
        data[account_type] = rate
        self._write_data(data)


class ApiInterestDataSource(InterestDataSource):
    """Implementation of interest data source using an external API"""

    def __init__(self, api_client):
        self.api_client = api_client

    def get(self, account_type: str) -> Optional[float]:
        """Get interest rate for a specific account type from API"""
        response = self.api_client.get_interest_rate(account_type)
        if response and 'rate' in response:
            return response['rate']
        return None

    def set(self, account_type: str, rate: float) -> None:
        """Set interest rate for a specific account type via API"""
        self.api_client.set_interest_rate(account_type, rate)


class ConfigInterestDataSource(InterestDataSource):
    """Implementation of interest data source using application config"""

    def __init__(self, config):
        self.config = config

    def get(self, account_type: str) -> Optional[float]:
        """Get interest rate from config"""
        config_key = f"interest.rates.{account_type}"
        return self.config.get(config_key)

    def set(self, account_type: str, rate: float) -> None:
        """Set interest rate in config"""
        config_key = f"interest.rates.{account_type}"
        self.config.set(config_key, rate)