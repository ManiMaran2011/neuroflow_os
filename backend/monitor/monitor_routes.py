from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime

from backend.db.database import get_db
from backend.db.models import Execution, ExecutionTimeline
from backend.utils.email import send_email

router = APIRouter(
    prefix="/monitor",
    tags=["monitor"]
)

# ================================
# SYSTEM TOKEN (CRON ONLY)
# ================================
def verify_system_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ")[1]
    if token != "SYSTEM_MONITOR_TOKEN":
        raise HTTPException(status_code=401, detail="Invalid system token")


# ================================
# DAILY MONITOR (CRON ENTRYPOINT)
# ================================
@router.post("/run-daily", dependencies=[Depends(verify_system_token)])
def run_daily_monitor(db: Session = Depends(get_db)):
    """
    Runs daily monitoring for all ACTIVE tracking executions.
    Called by cron (Render / GitHub Actions).
    """

    today = datetime.utcnow().date().isoformat()

    # 🔍 Fetch only ACTIVE executions
    executions = (
        db.query(Execution)
        .filter(Execution.status == "active")
        .all()
    )

    results = []

    for execution in executions:
        params = execution.params or {}

        # 🚫 Skip non-tracking executions
        if params.get("execution_type") != "tracking":
            continue

        last_completed = params.get("last_completed")

        # ✅ Already done today → no action
        if last_completed == today:
            results.append({
                "execution_id": execution.id,
                "status": "already_completed"
            })
            continue

        # 🔔 SEND REMINDER
        send_email(
            to_email=execution.user_email,
            subject="NeuroFlow Reminder ⏰",
            body=(
                "Hey 👋\n\n"
                "You haven’t completed today’s task yet.\n\n"
                "Open NeuroFlow and tap **Mark Done** to earn XP ⚡\n\n"
                "— NeuroFlow OS"
            )
        )

        # 🧠 TIMELINE LOG
        db.add(
            ExecutionTimeline(
                execution_id=execution.id,
                message="Daily reminder sent by MonitorAgent"
            )
        )

        results.append({
            "execution_id": execution.id,
            "status": "reminded"
        })

    db.commit()

    return {
        "status": "monitor_completed",
        "date": today,
        "checked_executions": len(results),
        "results": results
    }


