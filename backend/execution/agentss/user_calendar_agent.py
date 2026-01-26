from datetime import datetime
from backend.db.models import GoogleOAuthToken
from backend.utils.google_calendar import create_calendar_event


class CalendarAgent:
    async def run(self, user_input: str, params: dict):
        """
        Creates a Google Calendar event.
        """

        # -------- Validate input --------
        title = params.get("title", "NeuroFlow Event")
        start = params.get("start")
        end = params.get("end")

        if not start or not end:
            return {
                "status": "error",
                "effect": "missing_time",
                "summary": "Could not determine event time",
                "data": params,
            }

        # -------- Fetch OAuth token --------
        user_email = params.get("user_email")
        if not user_email:
            return {
                "status": "error",
                "effect": "missing_user",
                "summary": "User email not provided to CalendarAgent",
                "data": {},
            }

        token = params.get("google_token")
        if not token:
            return {
                "status": "error",
                "effect": "calendar_not_connected",
                "summary": "Google Calendar not connected",
                "data": {},
            }

        # -------- Create calendar event --------
        try:
            event = create_calendar_event(
                access_token=token,
                title=title,
                start=start,
                end=end,
            )

            return {
                "status": "success",
                "effect": "calendar_event_created",
                "summary": f"Event scheduled from {start} to {end}",
                "data": {
                    "event_id": event.get("id"),
                    "html_link": event.get("htmlLink"),
                    "start": start,
                    "end": end,
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "effect": "calendar_error",
                "summary": "Failed to create calendar event",
                "data": {
                    "error": str(e),
                },
            }

