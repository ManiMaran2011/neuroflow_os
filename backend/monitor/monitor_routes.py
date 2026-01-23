from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.db.database import get_db
from backend.db.models import Execution, ExecutionTimeline, UserStreak, User
from backend.execution.execution_routes import evaluate_progress

router = APIRouter(
    prefix="/monitor",
    tags=["monitor"]
)

# ----------------------------------------
# DAILY MONITOR (SYSTEM CRON)
# ----------------------------------------
@router.post("/run-daily")
def run_daily_monitor(db: Session = Depends(get_db)):
    """
    System-level daily monitor.
    Intended to be triggered by CRON (Render / GitHub Actions).
    No user authentication.
    """

    now = datetime.utcnow()
    today = now.date()

    results = []

    # ----------------------------------------
    # LOOP THROUGH ALL USERS
    # ----------------------------------------
    users = db.query(User).all()

    for user in users:
        user_email = user.email

        # ----------------------------------------
        # FIND RECENT EXECUTIONS (LAST 7 DAYS)
        # ----------------------------------------
        executions = db.query(Execution).filter(
            Execution.user_email == user_email,
            Execution.created_at >= now - timedelta(days=7)
        ).order_by(Execution.created_at.desc()).all()

        if not executions:
            continue

        # ----------------------------------------
        # BUILD EXECUTION HISTORY (MINIMAL)
        # ----------------------------------------
        execution_history = []

        for e in executions:
            execution_history.append({
                "date": e.created_at.date().isoformat(),
                "status": "completed" if e.status == "completed" else "missed"
            })

        # ----------------------------------------
        # FAKE PLAN CONTEXT (FOR NOW)
        # (Later this comes from Plans table)
        # ----------------------------------------
        plan = {
            "intent": "auto_monitored_plan",
            "created_at": executions[-1].created_at.isoformat()
        }

        # ----------------------------------------
        # REUSE EXISTING PROGRESS EVALUATION
        # ----------------------------------------
        evaluation_payload = {
            "plan": plan,
            "execution_history": execution_history
        }

        result = evaluate_progress(
            payload=evaluation_payload,
            db=db,
            user_email=user_email
        )

        results.append({
            "user": user_email,
            "result": result
        })

    return {
        "status": "monitor_completed",
        "run_date": today.isoformat(),
        "users_processed": len(results),
        "details": results
    }
