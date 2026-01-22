import os
import requests
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import GoogleOAuthToken
from backend.auth.jwt_handler import verify_token

router = APIRouter(prefix="/oauth", tags=["google-oauth"])

# ------------------------
# ENV VARS
# ------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_REDIRECT_URI = os.getenv(
    "FRONTEND_REDIRECT_URI",
    "https://neuroflow-ui.vercel.app"
)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events"
]

# ----------------------------------------
# CONNECT GOOGLE CALENDAR
# ----------------------------------------
@router.get("/google/connect")
def connect_google_calendar(
    token: str = Query(...),
):
    if not GOOGLE_CLIENT_ID or not GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    # 🔐 MANUALLY VERIFY JWT
    payload = verify_token(token)
    user_email = payload.get("sub")

    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token")

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": user_email,
    }

    auth_url = requests.Request(
        "GET",
        GOOGLE_AUTH_URL,
        params=params
    ).prepare().url

    return RedirectResponse(auth_url)


# ----------------------------------------
# GOOGLE OAUTH CALLBACK
# ----------------------------------------
@router.get("/callback")
def google_oauth_callback(
    code: str,
    state: str,  # user_email
    db: Session = Depends(get_db)
):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    token_data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }

    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Google token")

    token_json = token_response.json()

    expires_at = datetime.utcnow() + timedelta(
        seconds=token_json.get("expires_in", 3600)
    )

    existing = db.query(GoogleOAuthToken).filter(
        GoogleOAuthToken.user_email == state
    ).first()

    if existing:
        existing.access_token = token_json["access_token"]
        existing.refresh_token = token_json.get(
            "refresh_token", existing.refresh_token
        )
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

    # ✅ Redirect back to frontend
    return RedirectResponse(
        url=f"{FRONTEND_REDIRECT_URI}?calendar=connected"
    )



