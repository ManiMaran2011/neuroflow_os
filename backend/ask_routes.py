from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.auth.jwt_handler import get_current_user
from backend.execution.execution_service import create_execution
from backend.planner import create_plan

router = APIRouter(tags=["ask"])


@router.post("/ask")
async def ask(
    payload: dict,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user),
):
    # ---------------- VALIDATION ----------------
    user_input = payload.get("user_input")
    if not user_input or not isinstance(user_input, str):
        raise HTTPException(status_code=400, detail="Input missing")

    # ---------------- PLANNING ----------------
    try:
        plan = await create_plan(user_input)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Planner failed: {str(e)}"
        )

    if not plan or not isinstance(plan, dict):
        raise HTTPException(
            status_code=500,
            detail="Planner returned invalid plan"
        )

    # ---------------- ENRICH PLAN ----------------
    plan.setdefault("params", {})
    plan["params"]["user_email"] = user_email

    # ---------------- CREATE EXECUTION ----------------
    execution = create_execution(
        db=db,
        user_email=user_email,
        plan=plan
    )

    return {
        "status": "planned",
        "execution_id": execution.id,
        "execution_plan": plan
    }






