from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.db.database import get_db
from backend.db.models import Execution, ExecutionTimeline, UserStreak
from backend.utils.email import send_email

router = APIRouter(
    prefix="/monitor",
    tags=["monitor"]
)

# ================================
# SIMPLE SYSTEM TOKEN CHECK
# ================================
def verify_system_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ")[1]
    expected = "SYSTEM_MONITOR_TOKEN"

    if token != expected:
        raise HTTPException(status_code=401, detail="Invalid system token")


# ================================
# EVALUATE PROGRESS (INTERNAL)
# ================================
@router.post("/evaluate-progress")
def evaluate_progress(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Evaluates user progress for long-running plans
    (fitness, habits, learning, etc.)
    """

    user_email = payload.get("user_email")
    plan = payload.get("plan")
    history = payload.get("execution_history", [])

    if not user_email or not plan:
        raise HTTPException(status_code=400, detail="Invalid payload")

    missed = [h for h in history if h.get("status") == "missed"]
    consecutive_misses = len(missed)

    action_taken = "progress_ok"
    message = "User is on track"
    xp_gained = 5

    if consecutive_misses >= 2:
        action_taken = "monitor_nudge"
        message = "User missed multiple days"
        xp_gained = -5

        # 📧 EMAIL NUDGE
        send_email(
            to_email=user_email,
            subject="NeuroFlow check-in 👀",
            body=(
                "Hey 👋\n\n"
                "We noticed you've missed a few days.\n"
                "No pressure — just checking in 💙\n\n"
                "You’ve got this.\n"
                "— NeuroFlow OS"
            )
        )

    # --------------------
    # CREATE EXECUTION LOG
    # --------------------
    execution = Execution(
        user_email=user_email,
        intent=plan.get("intent", "progress_monitoring"),
        actions=action_taken,
        agents="MonitorAgent",
        params={
            "plan": plan,
            "history": history
        },
        status="completed",
        requires_approval=False,
        xp_gained=xp_gained
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    timeline = ExecutionTimeline(
        execution_id=execution.id,
        message=message
    )

    db.add(timeline)

    # --------------------
    # STREAK MANAGEMENT
    # --------------------
    now = datetime.utcnow()
    today = now.date()

    streak = db.query(UserStreak).filter(
        UserStreak.user_email == user_email
    ).first()

    if not streak:
        streak = UserStreak(
            user_email=user_email,
            current_streak=1,
            last_active_date=now
        )
        db.add(streak)
    else:
        last_date = (
            streak.last_active_date.date()
            if streak.last_active_date else None
        )

        if last_date == today:
            pass
        elif last_date == today - timedelta(days=1):
            streak.current_streak += 1
            streak.last_active_date = now
        else:
            streak.current_streak = 1
            streak.last_active_date = now

    db.commit()

    return {
        "status": "evaluated",
        "execution_id": execution.id,
        "action_taken": action_taken,
        "xp_gained": xp_gained,
        "current_streak": streak.current_streak
    }


# ================================
# DAILY MONITOR (CRON ENTRYPOINT)
# ================================
@router.post("/run-daily", dependencies=[Depends(verify_system_token)])
def run_daily_monitor(db: Session = Depends(get_db)):
    """
    Runs daily monitoring for all users.
    Called by cron (GitHub Actions / Render).
    """

    executions = db.query(Execution).all()
    users = list({e.user_email for e in executions if e.user_email})

    results = []

    for user_email in users:
        history = (
            db.query(Execution)
            .filter(Execution.user_email == user_email)
            .order_by(Execution.created_at.desc())
            .limit(3)
            .all()
        )

        execution_history = [
            {"status": "completed"} for _ in history
        ]

        payload = {
            "user_email": user_email,
            "plan": {
                "intent": "ongoing_monitoring"
            },
            "execution_history": execution_history
        }

        result = evaluate_progress(payload, db)
        results.append(result)

    return {
        "status": "monitor_completed",
        "run_date": datetime.utcnow().date().isoformat(),
        "users_processed": len(users),
        "details": results
    }

