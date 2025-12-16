from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"


class BaseAgent:
    def __init__(self, db_filename: str, name: str):
        self.name = name
        self.db_path = DATABASE_DIR / db_filename
        DATABASE_DIR.mkdir(exist_ok=True)
        if not self.db_path.exists():
            self.db_path.write_text("{}")

