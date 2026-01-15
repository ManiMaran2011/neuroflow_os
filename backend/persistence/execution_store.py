import json
import os
from typing import Dict, List
from backend.persistence.models import ExecutionRecord

DB_PATH = "backend/database/executions.json"


class ExecutionStore:
    @staticmethod
    def _load_db() -> Dict[str, dict]:
        if not os.path.exists(DB_PATH):
            return {}
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _save_db(data: Dict[str, dict]) -> None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def save(cls, execution: ExecutionRecord) -> None:
        db = cls._load_db()
        db[execution.execution_id] = execution.to_dict()
        cls._save_db(db)

    @classmethod
    def get(cls, execution_id: str) -> dict | None:
        db = cls._load_db()
        return db.get(execution_id)

    @classmethod
    def list_for_user(cls, user_id: str) -> List[dict]:
        db = cls._load_db()
        return [
            e for e in db.values()
            if e["user_id"] == user_id
        ]


