from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import requests
import json

from backend.db.database import get_db
from backend.db.models import GoogleOAuthToken
from backend.auth.jwt_handler import get_current_user
from backend.utils.llm import ask_llm  

router = APIRouter(prefix="/calendar", tags=["calendar"])

GOOGLE_CALENDAR_EVENTS_URL = (
    "https://www.googleapis.com/calendar/v3/calendars/primary/events"
)

# ---------------------------------------------------
# CREATE CALENDAR EVENT (STRUCTURED INPUT)
# ---------------------------------------------------
@router.post("/create-event")
def create_calendar_event(
    payload: dict,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    """
    Creates a Google Calendar event for the authenticated user.
    """

    token = db.query(GoogleOAuthToken).filter(
        GoogleOAuthToken.user_email == user_email
    ).first()

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Google Calendar not connected for user"
        )

    event_body = {
        "summary": payload.get("title", "Agent Scheduled Event"),
        "description": payload.get("description", ""),
        "start": {
            "dateTime": payload["start_time"],
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": payload["end_time"],
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

    return {
        "status": "event_created",
        "calendar_event": response.json(),
    }


# ---------------------------------------------------
# CREATE EVENT FROM NATURAL LANGUAGE (LLM POWERED)
# ---------------------------------------------------
@router.post("/from-text")
async def create_event_from_text(
    payload: dict,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    """
    Accepts natural language and schedules a calendar event.
    """

    user_text = payload.get("text")
    if not user_text:
        raise HTTPException(status_code=400, detail="Missing text input")

    prompt = f"""
You are an assistant that extracts calendar events.

Return ONLY valid JSON in this format:

{{
  "title": "string",
  "description": "string",
  "start_time": "YYYY-MM-DDTHH:MM:SS",
  "end_time": "YYYY-MM-DDTHH:MM:SS"
}}

Text:
{user_text}
"""

    llm_response = await ask_llm(prompt)

    try:
        event_data = json.loads(llm_response)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="LLM failed to return valid JSON"
        )

    # Reuse existing deterministic execution
    return create_calendar_event(
        payload=event_data,
        db=db,
        user_email=user_email
    )

