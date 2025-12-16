import json
from ..base_agent import BaseAgent

class ContactAgent(BaseAgent):
    def __init__(self):
        super().__init__("contacts_db.json", "ContactAgent")

    async def run(self, instruction: str):
        with open(self.db_path, "r") as f:
            data = json.load(f)

        contact_id = str(len(data) + 1)
        data[contact_id] = {"contact": instruction}

        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

        return f"Contact saved: {instruction}"
