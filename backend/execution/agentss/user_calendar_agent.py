from sqlalchemy.orm import Session
from fastapi import HTTPException
import requests

from backend.db.models import GoogleOAuthToken

GOOGLE_CALENDAR_EVENTS_URL = (
    "https://www.googleapis.com/calendar/v3/calendars/primary/events"
)


def execute_calendar_action(
    *,
    db: Session,
    user_email: str,
    action: dict,
):
    token = db.query(GoogleOAuthToken).filter(
        GoogleOAuthToken.user_email == user_email
    ).first()

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Google Calendar not connected for user"
        )

    event_body = {
        "summary": action.get("summary", "NeuroFlow Event"),
        "description": action.get("description", ""),
        "start": {
            "dateTime": action["start_time"],
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": action["end_time"],
            "timeZone": "Asia/Kolkata",
        },
    }

    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        GOOGLE_CALENDAR_EVENTS_URL,
        headers=headers,
        json=event_body,
    )

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=400,
            detail=f"Google Calendar error: {response.text}"
        )

    return response.json()
