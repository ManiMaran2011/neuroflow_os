import json
from pathlib import Path

class XPAgent:
    name = "XPAgent"

    def __init__(self):
        self.file_path = Path("database/xp_db.json")

    def _load(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    def _calculate_level(self, xp):
        if xp < 50:
            return 1
        if xp < 150:
            return 2
        if xp < 300:
            return 3
        return 4

    async def reward(self):
        data = self._load()
        data["xp"] += 10
        data["level"] = self._calculate_level(data["xp"])
        self._save(data)

        return {
            "agent": self.name,
            "status": "success",
            "message": f"XP +10 (Level {data['level']})",
            "data": data
        }





