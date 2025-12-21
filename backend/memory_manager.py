import json
import os
from datetime import datetime

MEMORY_PATH = os.path.join("database", "memory.json")


class MemoryManager:
    def __init__(self):
        if not os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "w") as f:
                json.dump({"users": {}}, f)

    def _load(self):
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(MEMORY_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def get_user(self, user_id):
        data = self._load()
        if user_id not in data["users"]:
            data["users"][user_id] = {
                "preferences": {},
                "executions": []
            }
            self._save(data)
        return data["users"][user_id]

    def store_execution(self, user_id, user_input, execution_plan, timeline):
        data = self._load()
        user = self.get_user(user_id)

        user["executions"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_input": user_input,
            "execution_plan": execution_plan,
            "timeline": timeline
        })

        data["users"][user_id] = user
        self._save(data)

    def get_last_execution(self, user_id):
        user = self.get_user(user_id)
        if not user["executions"]:
            return None
        return user["executions"][-1]


