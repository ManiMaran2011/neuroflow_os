from utils.telegram import send_telegram_message

class NotificationAgent:
    name = "NotificationAgent"

    async def run(self, user_input: str):
        send_telegram_message(f"⏰ Reminder created: {user_input}")

        return {
            "agent": self.name,
            "status": "success",
            "message": "Notification sent",
            "data": {
                "text": user_input
            }
        }


