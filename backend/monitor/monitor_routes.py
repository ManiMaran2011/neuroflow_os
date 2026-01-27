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
    Triggered by Render cron.
    """

    today = datetime.utcnow().date().isoformat()

    # 🔍 Fetch ACTIVE tracking executions
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

        # ✅ Already completed today → no reminder
        if last_completed == today:
            results.append({
                "execution_id": execution.id,
                "status": "already_completed_today"
            })
            continue

        # --------------------------------
        # 📧 ACTIONABLE EMAIL (MARK DONE)
        # --------------------------------
        base_url = "https://neuroflow-os.onrender.com"

        mark_done_url = (
            f"{base_url}/executions/"
            f"{execution.id}/mark-done"
        )

        subject = "🧠 NeuroFlow Daily Check-in"

        body = f"""
        <p>Hey 👋</p>

        <p><strong>Did you complete today’s goal?</strong></p>

        <p>
          <a href="{mark_done_url}"
             style="
               display:inline-block;
               padding:12px 18px;
               background:#16a34a;
               color:white;
               text-decoration:none;
               border-radius:8px;
               font-weight:600;
             ">
             ✅ Mark Done
          </a>
        </p>

        <p style="margin-top:12px;color:#666;font-size:14px;">
          Click once to log your progress and earn XP ⚡
        </p>

        <p style="margin-top:20px;">
          — NeuroFlow OS
        </p>
        """

        # 🔔 SEND EMAIL
        send_email(
            to_email=execution.user_email,
            subject=subject,
            body=body
        )

        # 🧠 TIMELINE LOG
        db.add(
            ExecutionTimeline(
                execution_id=execution.id,
                message="Daily progress check-in email sent"
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


