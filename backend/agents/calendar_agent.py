import json
from ..base_agent import BaseAgent

class CalendarAgent(BaseAgent):
    def __init__(self):
        super().__init__("calendar_db.json", "CalendarAgent")

    async def run(self, instruction: str):
        with open(self.db_path, "r") as f:
            data = json.load(f)

        event_id = str(len(data) + 1)
        data[event_id] = {"event": instruction}

        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

        return f"Calendar event added: {instruction}"

