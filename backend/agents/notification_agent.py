import json
from ..base_agent import BaseAgent

class NotificationAgent(BaseAgent):
    def __init__(self):
        super().__init__("notifications_db.json", "NotificationAgent")

    async def run(self, instruction: str):
        with open(self.db_path, "r") as f:
            data = json.load(f)

        notif_id = str(len(data) + 1)
        data[notif_id] = {"notification": instruction}

        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

        return f"Notification scheduled: {instruction}"

