import os
import requests

from backend.agents.base_agent import BaseAgent


class NotificationAgent(BaseAgent):
    name = "NotificationAgent"

    async def run(self, user_input: str, params: dict) -> dict:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            return {
                "status": "failed",
                "reason": "Missing env vars",
                "token_present": bool(token),
                "chat_id_present": bool(chat_id),
            }

        title = params.get("title", "NeuroFlow Task")
        start = params.get("start", "N/A")

        message = (
            "🔔 NeuroFlow Notification\n\n"
            f"Task/Event: {title}\n"
            f"Scheduled at: {start}"
        )

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
        }

        response = requests.post(url, json=payload, timeout=10)

        return {
            "status": "sent",
            "telegram_status_code": response.status_code,
        }






