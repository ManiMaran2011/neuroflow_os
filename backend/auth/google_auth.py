from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import os

from backend.auth.jwt_handler import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class GoogleAuthRequest(BaseModel):
    id_token: str

@router.post("/google")
def google_login(req: GoogleAuthRequest):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google client ID not configured")

    try:
        idinfo = id_token.verify_oauth2_token(
            req.id_token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        email_verified = idinfo.get("email_verified")

        if not email or not email_verified:
            raise HTTPException(status_code=401, detail="Unverified Google account")

        # 🔐 ISSUE SAME JWT AS NORMAL LOGIN
        access_token = create_access_token(
            data={"sub": email}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "email": email
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
