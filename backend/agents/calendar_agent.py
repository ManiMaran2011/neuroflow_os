import json
import os
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build

from backend.agents.base_agent import BaseAgent

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class CalendarAgent(BaseAgent):
    name = "CalendarAgent"

    async def run(self, user_input=None, params=None) -> dict:
        service_account_info = json.loads(
            os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        )

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES,
        )

        service = build("calendar", "v3", credentials=credentials)

        start = params.get("start")
        end = params.get("end")

        # fallback (demo-safe)
        if not start:
            start_dt = datetime.utcnow() + timedelta(minutes=5)
            end_dt = start_dt + timedelta(hours=1)
            start = start_dt.isoformat() + "Z"
            end = end_dt.isoformat() + "Z"

        event = {
            "summary": params.get("title", "NeuroFlow Task"),
            "start": {
                "dateTime": start,
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end,
                "timeZone": "UTC",
            },
        }

        created_event = service.events().insert(
            calendarId=os.environ["GOOGLE_CALENDAR_ID"],
            body=event
        ).execute()

        return {
            "agent": self.name,
            "action": "calendar_event_created",
            "event_id": created_event["id"],
            "htmlLink": created_event["htmlLink"],
        }









