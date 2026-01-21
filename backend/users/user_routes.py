from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.db.database import get_db
from backend.db.models import Execution, UserStreak
from backend.auth.jwt_handler import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# ----------------------------------------
# GET USER STATS (XP + STREAK)
# ----------------------------------------
@router.get("/me/stats")
def get_my_stats(
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    total_xp = db.query(
        func.coalesce(func.sum(Execution.xp_gained), 0)
    ).filter(
        Execution.user_email == user_email
    ).scalar()

    streak = db.query(UserStreak).filter(
        UserStreak.user_email == user_email
    ).first()

    return {
        "total_xp": total_xp,
        "current_streak": streak.current_streak if streak else 0
    }
