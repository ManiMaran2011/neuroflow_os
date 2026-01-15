from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth.jwt_handler import get_current_user
from backend.db.database import get_db
from backend.planner import create_plan
from backend.execution.execution_service import create_execution
from backend.parent_agent import ParentAgent


router = APIRouter(
    prefix="/ask",
    tags=["ask"]
)


# ---------------------------
# Request Schema
# ---------------------------
class AskRequest(BaseModel):
    user_input: str
    approved: bool = False


# ---------------------------
# Ask Route
# ---------------------------
@router.post("")
async def ask(
    req: AskRequest,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1️⃣ CREATE EXECUTION PLAN (IMPORTANT: await)
    plan = await create_plan(req.user_input)

    # 2️⃣ CREATE EXECUTION (persisted to DB)
    execution = create_execution(
        db=db,
        user_email=user_email,
        plan=plan
    )

    # 3️⃣ APPROVAL GATE
    if execution.requires_approval and not req.approved:
        return {
            "status": "awaiting_approval",
            "execution_id": execution.id,
            "execution_plan": plan
        }

    # 4️⃣ EXECUTE VIA PARENT AGENT
    parent_agent = ParentAgent()
    result = await parent_agent.handle(
        db=db,
        execution=execution,
        execution_plan=plan,
        user_input=req.user_input
    )

    return {
        "status": "executed",
        "execution_id": execution.id,
        "result": result
    }




