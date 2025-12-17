from base_agent import BaseAgent
import json
import os

class XPAgent(BaseAgent):
    name = "XPAgent"

    def __init__(self):
        self.db_path = "backend/database/xp_db.json"

    async def run(self, user_input: str):
        data = {"xp": "increased"}

        if self.db_path:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, "w") as f:
                json.dump(data, f)

        return {
            "agent": self.name,
            "status": "success",
            "message": "XP increased",
            "data": data
        }




