from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.db.database import get_db
from backend.db.models import Execution, ExecutionTimeline
from backend.utils.magic_links import verify_magic_token
from fastapi.responses import HTMLResponse

router = APIRouter(
    prefix="/magic",
    tags=["magic"]
)


@router.get("/mark-done", response_class=HTMLResponse)
def magic_mark_done(token: str, db: Session = Depends(get_db)):
    """
    One-click progress confirmation from email.
    No login required.
    """

    try:
        data = verify_magic_token(token)
    except ValueError as e:
        return HTMLResponse(
            f"<h3>❌ {str(e)}</h3>",
            status_code=400
        )

    execution_id = data["execution_id"]
    user_email = data["user_email"]

    execution = (
        db.query(Execution)
        .filter(
            Execution.id == execution_id,
            Execution.user_email == user_email
        )
        .first()
    )

    if not execution:
        return HTMLResponse(
            "<h3>❌ Execution not found</h3>",
            status_code=404
        )

    today = datetime.utcnow().date().isoformat()

    # Already done today
    if execution.params.get("last_completed") == today:
        return HTMLResponse("""
            <h2>✅ Already done!</h2>
            <p>You already completed today’s goal.</p>
        """)

    # Mark done
    execution.params["last_completed"] = today
    execution.xp_gained += 5

    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message="Marked done via magic link (+5 XP)"
        )
    )

    db.commit()

    return HTMLResponse("""
        <h2>🎉 Nice work!</h2>
        <p>Your progress for today is recorded.</p>
        <p><strong>+5 XP earned ⚡</strong></p>
        <p>You can close this tab.</p>
    """)
