from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import Execution, ExecutionTimeline
from backend.auth.jwt_handler import get_current_user
from backend.execution.execution_service import approve_execution

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

    # 🔥 ADD THESE TWO (THIS IS THE FIX)
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
# LOG EXECUTION (AGENT / SYSTEM)
# ----------------------------------------
@router.post("/log")
async def log_execution_from_agent(payload: dict, db: Session = Depends(get_db)):
    """
    Receives execution logs from agentic systems (Dify).
    No user auth — system-level logging.
    """

    execution = Execution(
        user_email=payload.get("user_email", "system"),
        intent=payload.get("decision_source", "passive_monitoring"),
        actions=payload.get("action_taken"),
        agents=payload.get("channel"),
        params=payload,
        status="completed",
        estimated_tokens=payload.get("estimated_tokens"),
        estimated_cost=payload.get("estimated_cost"),
        xp_gained=payload.get("xp_gained", 0)
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    timeline = ExecutionTimeline(
        execution_id=execution.id,
        message="Execution logged from agent"
    )

    db.add(timeline)
    db.commit()

    return {
        "status": "logged",
        "execution_id": execution.id
    }






