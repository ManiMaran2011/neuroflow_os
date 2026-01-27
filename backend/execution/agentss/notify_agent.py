from backend.utils.email import send_email


class NotifyAgent:
    async def run(self, user_input: str, params: dict):
        """
        Sends an email notification (used by MonitorAgent decisions)
        """

        user_email = params.get("user_email")
        message = params.get("message", "")
        reason = params.get("reason", "")

        if not user_email:
            return {
                "status": "error",
                "effect": "missing_user",
                "summary": "No user email provided",
            }

        subject = "🔔 NeuroFlow Progress Check-in"
        body = (
            "Hey 👋\n\n"
            f"{message}\n\n"
            f"Reason: {reason}\n\n"
            "You’ve got this 💪\n\n"
            "— NeuroFlow OS"
        )

        try:
            send_email(
                to_email=user_email,
                subject=subject,
                body=body,
            )

            return {
                "status": "success",
                "effect": "notification_sent",
                "channel": "email",
                "to": user_email,
            }

        except Exception as e:
            return {
                "status": "error",
                "effect": "email_failed",
                "error": str(e),
            }



