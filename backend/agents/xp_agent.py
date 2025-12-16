import json
from ..base_agent import BaseAgent

class XPAgent(BaseAgent):
    def __init__(self):
        super().__init__("xp_db.json", "XPAgent")

    async def run(self, instruction: str):
        with open(self.db_path, "r") as f:
            data = json.load(f)

        data["xp"] = data.get("xp", 0) + 10

        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

        return "XP increased"


