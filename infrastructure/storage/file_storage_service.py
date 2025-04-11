import os
import json
from typing import Dict, Any, Optional


class FileStorageService:
    """A utility service for file-based storage operations"""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def get_storage_dir(self, entity_type: str) -> str:
        """Create and return storage directory for entity type"""
        storage_dir = os.path.join(self.base_dir, entity_type)
        os.makedirs(storage_dir, exist_ok=True)
        return storage_dir

    def save_to_file(self, entity_id: str, entity_type: str, data: Dict[str, Any]) -> None:
        """Save data to file"""
        storage_dir = self.get_storage_dir(entity_type)
        file_path = os.path.join(storage_dir, f"{entity_id}.json")

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, entity_id: str, entity_type: str) -> Optional[Dict[str, Any]]:
        """Load data from file"""
        storage_dir = self.get_storage_dir(entity_type)
        file_path = os.path.join(storage_dir, f"{entity_id}.json")

        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def delete_file(self, entity_id: str, entity_type: str) -> bool:
        """Delete a file"""
        storage_dir = self.get_storage_dir(entity_type)
        file_path = os.path.join(storage_dir, f"{entity_id}.json")

        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def list_all_ids(self, entity_type: str) -> list[str]:
        """List all entity IDs of a specific type"""
        storage_dir = self.get_storage_dir(entity_type)

        if not os.path.exists(storage_dir):
            return []

        ids = []
        for filename in os.listdir(storage_dir):
            if filename.endswith('.json'):
                # Remove .json extension to get the ID
                entity_id = filename[:-5]
                ids.append(entity_id)

        return ids