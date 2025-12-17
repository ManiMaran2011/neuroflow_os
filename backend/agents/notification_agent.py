import json
import os

class NotificationAgent:
    name = "NotificationAgent"

    def __init__(self):
        self.db_path = "backend/database/notifications_db.json"

    async def run(self, user_input: str):
        data = {
            "notification": user_input
        }

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(data, f)

        return {
            "agent": self.name,
            "status": "success",
            "message": "Notification scheduled",
            "data": data
        }


