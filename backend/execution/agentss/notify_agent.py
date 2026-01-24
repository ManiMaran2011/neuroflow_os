from backend.utils.email import send_email
from backend.agents.base_agent import BaseAgent


class NotifyAgent(BaseAgent):
    name = "NotifyAgent"

    async def run(self, user_email: str, context: dict) -> dict:
        """
        Sends reminder + motivational email to user.
        """

        intent = context.get("intent", "general")
        missed_days = context.get("missed_days", 0)

        # -------------------------
        # MESSAGE LOGIC
        # -------------------------
        if missed_days >= 2:
            subject = "Let’s get back on track 💪"
            body = (
                f"Hey 👋\n\n"
                f"You’ve missed {missed_days} days recently.\n"
                f"No stress — progress isn’t about perfection.\n\n"
                f"Do one small thing today and you’re back in the game 🚀\n\n"
                f"— NeuroFlow"
            )
            action = "motivational_nudge_sent"

        else:
            subject = "Quick reminder ⏰"
            body = (
                f"Hey 👋\n\n"
                f"Just checking in — did you complete today’s task?\n\n"
                f"Consistency beats intensity 💯\n\n"
                f"— NeuroFlow"
            )
            action = "reminder_sent"

        # -------------------------
        # SEND EMAIL
        # -------------------------
        send_email(
            to_email=user_email,
            subject=subject,
            body=body
        )

        return {
            "agent": self.name,
            "action": action,
            "channel": "email",
            "user_email": user_email
        }

