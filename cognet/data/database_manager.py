import json
import os

class DatabaseManager:
    def __init__(self, filepath="cognet_db.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self.save_data([])

    def load_data(self) -> list:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_data(self, data: list):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving database: {e}")