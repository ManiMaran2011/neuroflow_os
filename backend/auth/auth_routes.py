from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.db.database import get_db
from backend.db.models import User
from backend.auth.jwt_handler import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


class LoginRequest(BaseModel):
    email: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    email = data.email.lower().strip()

    # 🔥 AUTO-CREATE USER IF NOT EXISTS
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token
    }




