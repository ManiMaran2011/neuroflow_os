from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = None

    # Load saved token if it exists
    if os.path.exists("backend/token.json"):
        creds = Credentials.from_authorized_user_file(
            "backend/token.json", SCOPES
        )

    # If no valid creds, start OAuth flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "backend/credentials.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)

        # Save token for future runs
        with open("backend/token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def create_event(event_data: dict):
    service = get_calendar_service()

    event = {
        "summary": event_data["title"],
        "start": {
            "dateTime": event_data["start"],
            "timeZone": event_data.get("timezone", "Asia/Kolkata"),
        },
        "end": {
            "dateTime": event_data["end"],
            "timeZone": event_data.get("timezone", "Asia/Kolkata"),
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return {
        "event_id": created_event.get("id"),
        "html_link": created_event.get("htmlLink"),
    }
