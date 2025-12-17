import os
import json
from base_agent import BaseAgent


class CalendarAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CalendarAgent",
            db_path="backend/database/calendar_db.json"
        )

    async def run(self, user_input: str):
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Initialize DB file if missing
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump([], f)

        # Load existing calendar events
        with open(self.db_path, "r") as f:
            events = json.load(f)

        # Add new calendar event
        new_event = {"event": user_input}
        events.append(new_event)

        # Save back to DB
        with open(self.db_path, "w") as f:
            json.dump(events, f, indent=2)

        return {
            "agent": self.name,
            "status": "success",
            "message": "Calendar event added",
            "data": new_event
        }




