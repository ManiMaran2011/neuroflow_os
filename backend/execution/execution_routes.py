from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.db.database import get_db
from backend.db.models import Execution, ExecutionTimeline, UserStreak
from backend.auth.jwt_handler import get_current_user
from backend.execution.execution_service import approve_execution

# 🔥 NEW AGENTS
from backend.execution.agentss.monitor_agent import MonitorAgent
from backend.execution.agentss.evaluate_progress_agent import EvaluateProgressAgent

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
# 🔥 EVALUATE PROGRESS (MONITOR + LLM)
# ----------------------------------------
@router.post("/evaluate-progress")
async def evaluate_progress(
    payload: dict,
    user_email: str = Depends(get_current_user),
):
    """
    Evaluates user progress on a plan and decides
    whether the system should act (no execution yet).
    """

    plan = payload.get("plan")
    execution_history = payload.get("execution_history", [])

    if not plan:
        raise HTTPException(status_code=400, detail="Missing plan")

    monitor = MonitorAgent()
    evaluator = EvaluateProgressAgent()

    # --------------------
    # STEP 1: MONITOR
    # --------------------
    monitor_result = await monitor.run(
        plan=plan,
        execution_history=execution_history,
        now=datetime.utcnow(),
    )

    if not monitor_result.get("action_needed"):
        return {
            "status": "no_action",
            "agent": "MonitorAgent",
            "reason": monitor_result.get("reason"),
        }

    # --------------------
    # STEP 2: EVALUATE (LLM)
    # --------------------
    evaluation = await evaluator.run(
        plan=plan,
        execution_history=execution_history,
    )

    return {
        "status": "evaluation_complete",
        "user": user_email,
        "monitor": monitor_result,
        "evaluation": evaluation,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ----------------------------------------
# LOG EXECUTION (AGENT / SYSTEM)
# ----------------------------------------
@router.post("/log")
async def log_execution_from_agent(payload: dict, db: Session = Depends(get_db)):
    """
    Receives execution logs from agentic systems.
    System-level logging (no user auth).
    """

    # --------------------
    # XP CALCULATION
    # --------------------
    action = payload.get("action_taken")

    XP_RULES = {
        "telegram_nudge_sent": 10,
        "calendar_event_created": 15,
    }

    xp_gained = XP_RULES.get(action, 0)

    # --------------------
    # CREATE EXECUTION
    # --------------------
    execution = Execution(
        user_email=payload.get("user_email", "system"),
        intent=payload.get("decision_source", "passive_monitoring"),
        actions=action,
        agents=payload.get("channel"),
        params=payload,
        status="completed",
        estimated_tokens=payload.get("estimated_tokens"),
        estimated_cost=payload.get("estimated_cost"),
        xp_gained=xp_gained
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # --------------------
    # EXECUTION TIMELINE
    # --------------------
    timeline = ExecutionTimeline(
        execution_id=execution.id,
        message="Execution logged from agent"
    )

    db.add(timeline)
    db.commit()

    # --------------------
    # STREAK TRACKING
    # --------------------
    now = datetime.utcnow()
    today = now.date()
    user_email = payload.get("user_email", "system")

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
            if streak.last_active_date
            else None
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
        "status": "logged",
        "execution_id": execution.id,
        "xp_gained": xp_gained,
        "current_streak": streak.current_streak
    }









