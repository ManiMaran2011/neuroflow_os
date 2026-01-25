from sqlalchemy.orm import Session
from backend.db.models import Execution, ExecutionTimeline, User
from backend.parent_agent import ParentAgent


# -------------------------
# SIMPLE COST ESTIMATION
# -------------------------
def estimate_cost(user_input: str):
    estimated_tokens = max(100, len(user_input.split()) * 10)
    estimated_cost = round((estimated_tokens / 1000) * 0.01, 4)
    return estimated_tokens, estimated_cost


# ------------------------------------------------
# CREATE EXECUTION
# ------------------------------------------------
def create_execution(db: Session, user_email: str, plan: dict) -> Execution:
    # ---------------- USER ----------------
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(email=user_email)
        db.add(user)
        db.commit()

    # ---------------- COST ----------------
    tokens, cost = estimate_cost(plan.get("reasoning", ""))

    # ---------------- NORMALIZE PLAN ----------------
    # Handles BOTH rule-based planner 

    actions = plan.get("actions")

    agents = plan.get("agents")

    params = plan.get("params")
    

    requires_approval = plan.get("requires_approval", False)

    # ---------------- EXECUTION ----------------
    execution = Execution(
        id=plan["plan_id"],
        user_email=user_email,
        intent=plan.get("intent", "llm_execution"),
        actions=actions,
        agents=agents,
        params=params,
        requires_approval=requires_approval,
        status="awaiting_approval" if requires_approval else "created",
        estimated_tokens=tokens,
        estimated_cost=cost
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # ---------------- TIMELINE ----------------
    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message=f"Execution created (Est. cost: ${cost})"
        )
    )
    db.commit()

    return execution


# ------------------------------------------------
# APPROVE EXECUTION
# ------------------------------------------------
async def approve_execution(db: Session, execution: Execution):
    execution.status = "executing"
    db.commit()

    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message="Execution approved by user"
        )
    )
    db.commit()

    parent_agent = ParentAgent()

    result = await parent_agent.handle(
        db=db,
        execution=execution,
        execution_plan={
            "intent": execution.intent,
            "actions": execution.actions,
            "agents": execution.agents,
            "params": execution.params
        },
        user_input=None
    )

    execution.status = "executed"
    db.commit()

    # ---------------- XP ----------------
    user = db.query(User).filter(User.email == execution.user_email).first()
    xp_awarded = 15

    if user:
        user.xp += xp_awarded
        db.commit()

        db.add(
            ExecutionTimeline(
                execution_id=execution.id,
                message=f"XP awarded: +{xp_awarded} (Total XP: {user.xp})"
            )
        )
        db.commit()

    return {
        "status": "executed",
        "execution_id": execution.id,
        "result": result,
        "xp_awarded": xp_awarded,
        "total_xp": user.xp if user else None,
        "estimated_tokens": execution.estimated_tokens,
        "estimated_cost": execution.estimated_cost
    }



