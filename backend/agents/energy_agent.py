import json
import os

class EnergyAgent:
    name = "EnergyAgent"

    def __init__(self):
        self.db_path = "backend/database/energy_db.json"

    async def run(self, user_input: str):
        data = {
            "energy_preference": user_input
        }

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(data, f)

        return {
            "agent": self.name,
            "status": "success",
            "message": "Energy preference updated",
            "data": data
        }



