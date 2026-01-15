from datetime import datetime
import os.path

from backend.agents.base_agent import BaseAgent

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class CalendarAgent(BaseAgent):
    name = "CalendarAgent"

    async def run(self, user_input=None, params=None) -> dict:
        creds = None

        base_dir = os.path.dirname(__file__)
        token_path = os.path.join(base_dir, "token.json")
        creds_path = os.path.join(base_dir, "credentials.json")

        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # If no valid creds, run OAuth flow
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

            # Save token
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": params.get("title", "NeuroFlow Event"),
            "start": {
                "dateTime": params["start"],
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": params["end"],
                "timeZone": "UTC",
            },
        }

        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        return {
            "agent": self.name,
            "action": "create_calendar_event",
            "event": {
                "id": created_event.get("id"),
                "title": created_event.get("summary"),
                "start": created_event["start"]["dateTime"],
                "end": created_event["end"]["dateTime"],
                "link": created_event.get("htmlLink"),
            }
        }








