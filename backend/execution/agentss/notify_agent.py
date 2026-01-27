from backend.utils.email import send_email


class NotifyAgent:
    """
    Sends real-world notifications (email).
    Used by MonitorAgent for daily progress check-ins.
    """

    async def run(self, user_input: str, params: dict):
        user_email = params.get("user_email")
        goal_id = params.get("goal_id")
        reason = params.get("reason", "")

        if not user_email or not goal_id:
            return {
                "status": "error",
                "summary": "Missing user_email or goal_id",
            }

        base_url = "https://neuroflow-os.onrender.com"

        yes_url = (
            f"{base_url}/progress/yes"
            f"?goal_id={goal_id}&email={user_email}"
        )
        no_url = (
            f"{base_url}/progress/no"
            f"?goal_id={goal_id}&email={user_email}"
        )

        subject = "🧠 NeuroFlow Daily Check-in"
        body = f"""
        <p>Hey 👋</p>

        <p><strong>Did you complete today’s goal?</strong></p>

        <p>
          <a href="{yes_url}">✅ Yes</a><br/>
          <a href="{no_url}">❌ No</a>
        </p>

        <p style="color: #666; font-size: 12px;">
          {reason}
        </p>

        <p>— NeuroFlow OS</p>
        """

        try:
            send_email(
                to_email=user_email,
                subject=subject,
                body=body,
            )

            return {
                "status": "success",
                "effect": "daily_checkin_sent",
                "channel": "email",
                "to": user_email,
            }

        except Exception as e:
            return {
                "status": "error",
                "effect": "email_failed",
                "error": str(e),
            }




