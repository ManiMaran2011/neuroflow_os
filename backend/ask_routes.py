from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.auth.jwt_handler import get_current_user
from backend.execution.execution_service import create_execution
from backend.parent_agent import ParentAgent
from backend.planner import create_plan  

router = APIRouter()


@router.post("/ask")
async def ask(
    payload: dict,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user),
):
    user_input = payload.get("input")

    if not user_input:
        raise HTTPException(status_code=400, detail="Input missing")

    # ✅ ALWAYS assign plan
    plan = await create_plan(user_input)

    # ✅ GUARANTEE params exists
    if "params" not in plan or plan["params"] is None:
        plan["params"] = {}

    # attach user context
    plan["params"]["user_email"] = user_email

    # ---------------- CREATE EXECUTION ----------------
    execution = create_execution(
        db=db,
        user_email=user_email,
        plan=plan,
    )

    # ---------------- AUTO EXECUTE IF NO APPROVAL ----------------
    if not execution.requires_approval:
        parent_agent = ParentAgent()
        await parent_agent.handle(
            db=db,
            execution=execution,
            execution_plan={
                "intent": execution.intent,
                "actions": execution.actions,
                "agents": execution.agents,
                "params": execution.params,
            },
            user_input=user_input,
        )

    return {
        "execution_id": execution.id,
        "execution_plan": plan,
    }





