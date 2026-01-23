from datetime import datetime

class NotificationAgent:
    name = "NotifyAgent"

    async def run(self, user_email: str, message: str, reason: str = None):
        """
        Simulated notification agent.
        In future this can send:
        - Email
        - Push
        - WhatsApp
        """

        # ---- SIMULATION ----
        notification = {
            "agent": self.name,
            "user_email": user_email,
            "message": message,
            "reason": reason,
            "sent_at": datetime.utcnow().isoformat(),
            "channel": "simulated"
        }

        return notification
