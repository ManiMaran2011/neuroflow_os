from backend.utils.email import send_email


class NotifyAgent:
    async def run(self, user_input: str, params: dict):
        """
        Sends an email notification / reminder.
        """

        user_email = params.get("user_email")
        reminder_time = params.get("reminder_time")

        if not user_email:
            return {
                "status": "error",
                "effect": "missing_user",
                "summary": "No user email provided for notification",
                "data": {},
            }

        subject = "⏰ NeuroFlow Reminder"
        body = (
            "Hey 👋\n\n"
            "Just a reminder about your upcoming task or meeting.\n\n"
            "You've got this 💪\n\n"
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
                "summary": "Reminder email sent successfully",
                "data": {
                    "channel": "email",
                    "to": user_email,
                    "scheduled_for": reminder_time,
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "effect": "email_failed",
                "summary": "Failed to send reminder email",
                "data": {
                    "error": str(e),
                },
            }


