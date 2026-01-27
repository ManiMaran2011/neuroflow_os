import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("MAGIC_LINK_SECRET", "dev-secret-change-me")
ALGORITHM = "HS256"


def create_magic_token(
    *,
    execution_id: str,
    user_email: str,
    action: str,
    expires_in_minutes: int = 60
) -> str:
    payload = {
        "execution_id": execution_id,
        "user_email": user_email,
        "action": action,
        "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_magic_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Magic link expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid magic link")
