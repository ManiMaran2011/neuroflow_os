from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.auth.jwt_handler import get_current_user
from backend.execution.agentss.user_calendar_agent import execute_calendar_action

router = APIRouter(prefix="/execute", tags=["execution"])


@router.post("/")
async def execute_plan(
    plan: dict,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user),
):
    """
    Executes a previously approved plan.
    """

    execution_channel = plan.get("execution_channel")

    if execution_channel == "calendar":
        result = execute_calendar_action(
            db=db,
            user_email=user_email,
            action=plan["action"],
        )

        return {
            "status": "executed",
            "channel": "calendar",
            "result": result,
        }

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported execution channel: {execution_channel}"
    )
