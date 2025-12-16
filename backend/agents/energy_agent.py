import json
from ..base_agent import BaseAgent

class EnergyAgent(BaseAgent):
    def __init__(self):
        super().__init__("energy_db.json", "EnergyAgent")

    async def run(self, instruction: str):
        with open(self.db_path, "r") as f:
            data = json.load(f)

        data["energy"] = instruction

        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

        return "Energy preference updated"

