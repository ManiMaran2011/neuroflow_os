from fastapi import APIRouter
from datetime import datetime
from backend.db.models import ProgressCheckIn
from backend.db.session import get_db

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/yes")
def progress_yes(goal_id: str, email: str, db=next(get_db())):
    db.add(
        ProgressCheckIn(
            user_email=email,
            goal_id=goal_id,
            completed=True,
            date=datetime.utcnow(),
        )
    )
    db.commit()
    return {"status": "recorded", "completed": True}


@router.get("/no")
def progress_no(goal_id: str, email: str, db=next(get_db())):
    db.add(
        ProgressCheckIn(
            user_email=email,
            goal_id=goal_id,
            completed=False,
            date=datetime.utcnow(),
        )
    )
    db.commit()
    return {"status": "recorded", "completed": False}
