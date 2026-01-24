from fastapi import APIRouter
from backend.utils.email import send_email

router = APIRouter(prefix="/test", tags=["email"])

@router.get("/email")
def test_email():
    send_email(
        to_email="m20maran@gmail.com",
        subject="NeuroFlow Email Test 🚀",
        body="If you got this, Resend email works perfectly."
    )
    return {"status": "email_sent"}

