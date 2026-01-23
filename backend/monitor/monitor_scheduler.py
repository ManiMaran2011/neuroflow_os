from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from backend.db.database import SessionLocal
from backend.db.models import Execution
from backend.execution.execution_routes import evaluate_progress

scheduler = BackgroundScheduler()

def run_daily_monitor():
    """
    Runs once per day.
    Evaluates progress for active executions.
    """
    db = SessionLocal()

    try:
        # Example: fetch recent executions (last 7 days)
        since = datetime.utcnow() - timedelta(days=7)

        executions = db.query(Execution).filter(
            Execution.created_at >= since
        ).all()

        for execution in executions:
            payload = {
                "plan": {
                    "intent": execution.intent,
                    "created_at": execution.created_at.isoformat()
                },
                "execution_history": [
                    {
                        "date": execution.created_at.date().isoformat(),
                        "status": execution.status
                    }
                ]
            }

            # System-level call (no auth)
            evaluate_progress(
                payload=payload,
                db=db,
                user_email=execution.user_email
            )

    finally:
        db.close()


def start_monitor_scheduler():
    scheduler.add_job(
        run_daily_monitor,
        trigger="cron",
        hour=9,   # every day at 9 AM UTC
        minute=0
    )
    scheduler.start()
