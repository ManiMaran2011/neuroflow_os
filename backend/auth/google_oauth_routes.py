from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import requests
from datetime import datetime, timedelta

from backend.db.database import get_db
from backend.db.models import GoogleOAuthToken
from backend.auth.jwt_handler import get_current_user
from backend.config import settings  # or however you load env vars

router = APIRouter(prefix="/oauth", tags=["google-oauth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events"
]


# ----------------------------------------
# CONNECT GOOGLE CALENDAR
# ----------------------------------------
@router.get("/google/connect")
def connect_google_calendar(user_email: str = Depends(get_current_user)):
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": user_email
    }

    auth_url = requests.Request("GET", GOOGLE_AUTH_URL, params=params).prepare().url
    return RedirectResponse(auth_url)


# ----------------------------------------
# GOOGLE OAUTH CALLBACK
# ----------------------------------------
@router.get("/callback")
def google_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    token_data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }

    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Google token")

    token_json = token_response.json()

    expires_at = datetime.utcnow() + timedelta(seconds=token_json["expires_in"])

    existing = db.query(GoogleOAuthToken).filter(
        GoogleOAuthToken.user_email == state
    ).first()

    if existing:
        existing.access_token = token_json["access_token"]
        existing.refresh_token = token_json.get("refresh_token", existing.refresh_token)
        existing.expires_at = expires_at
        existing.scope = "calendar"
    else:
        db.add(
            GoogleOAuthToken(
                user_email=state,
                access_token=token_json["access_token"],
                refresh_token=token_json.get("refresh_token"),
                expires_at=expires_at,
                scope="calendar"
            )
        )

    db.commit()

    return {
        "status": "connected",
        "message": "Google Calendar connected successfully"
    }
