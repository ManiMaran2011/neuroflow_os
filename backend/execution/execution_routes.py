from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.db.database import get_db
from backend.db.models import Execution, ExecutionTimeline, UserStreak
from backend.auth.jwt_handler import get_current_user
from backend.execution.execution_service import approve_execution

# 🔔 NEW AGENT
from backend.execution.agentss.notify_agent import NotifyAgent

router = APIRouter(
    prefix="/executions",
    tags=["executions"]
)

# ----------------------------------------
# GET EXECUTION DETAILS
# ----------------------------------------
@router.get("/{execution_id}")
def get_execution_details(
    execution_id: str,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    execution = db.query(Execution).filter(
        Execution.id == execution_id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.user_email != user_email:
        raise HTTPException(status_code=403, detail="Not authorized")

    timeline = db.query(ExecutionTimeline).filter(
        ExecutionTimeline.execution_id == execution.id
    ).order_by(ExecutionTimeline.created_at).all()

    return {
        "execution_id": execution.id,
        "user_email": execution.user_email,
        "intent": execution.intent,
        "actions": execution.actions,
        "agents": execution.agents,
        "params": execution.params,
        "status": execution.status,
        "requires_approval": execution.requires_approval,
        "created_at": execution.created_at,
        "estimated_tokens": execution.estimated_tokens,
        "estimated_cost": execution.estimated_cost,
        "xp_gained": execution.xp_gained,
        "timeline": [
            {
                "message": t.message,
                "created_at": t.created_at
            }
            for t in timeline
        ]
    }


# ----------------------------------------
# APPROVE EXECUTION
# ----------------------------------------
@router.post("/{execution_id}/approve")
async def approve_execution_api(
    execution_id: str,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    execution = db.query(Execution).filter(
        Execution.id == execution_id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.user_email != user_email:
        raise HTTPException(status_code=403, detail="Not authorized")

    if execution.status != "awaiting_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Execution is in '{execution.status}' state"
        )

    return await approve_execution(db, execution)


# ----------------------------------------
# EVALUATE PROGRESS (MONITOR → NOTIFY)
# ----------------------------------------
@router.post("/evaluate-progress")
async def evaluate_progress(
    payload: dict,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    """
    Evaluates user progress for long-running plans
    (habits, fitness, learning, etc.)
    """

    plan = payload.get("plan")
    history = payload.get("execution_history", [])

    if not plan:
        raise HTTPException(status_code=400, detail="Plan missing")

    # --------------------
    # RULE-BASED EVALUATION
    # --------------------
    missed_days = [
        h for h in history if h.get("status") == "missed"
    ]

    consecutive_misses = len(missed_days)

    action_taken = "progress_ok"
    message = "User is on track"
    xp_gained = 5

    if consecutive_misses >= 2:
        action_taken = "monitor_nudge"
        message = "You’ve missed a few days. Want help getting back on track?"
        xp_gained = -5

    # --------------------
    # 🔔 NOTIFY AGENT
    # --------------------
    notifier = NotifyAgent()
    notification_result = await notifier.run(
        user_email=user_email,
        message=message,
        reason="progress_evaluation"
    )

    # --------------------
    # CREATE EXECUTION
    # --------------------
    execution = Execution(
        user_email=user_email,
        intent=plan.get("intent", "progress_monitoring"),
        actions=action_taken,
        agents=["MonitorAgent", "NotifyAgent"],
        params={
            "plan": plan,
            "history": history,
            "notification": notification_result
        },
        status="completed",
        requires_approval=False,
        xp_gained=xp_gained
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # --------------------
    # TIMELINE ENTRY
    # --------------------
    timeline = ExecutionTimeline(
        execution_id=execution.id,
        message=f"NotifyAgent executed: {message}"
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
        "current_streak": streak.current_streak,
        "notification": notification_result
    }











