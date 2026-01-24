# backend/test_email_routes.py
from fastapi import APIRouter
from backend.utils.email import send_email

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/email")
def test_email():
    send_email(
        to_email="YOUR_PERSONAL_EMAIL@gmail.com",
        subject="NeuroFlow Email Test",
        body="If you got this, email setup works 🚀"
    )
    return {"status": "email_sent"}
