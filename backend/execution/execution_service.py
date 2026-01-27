from sqlalchemy.orm import Session
from backend.db.models import Execution, ExecutionTimeline, User
from backend.parent_agent import ParentAgent


# -------------------------
# SIMPLE COST ESTIMATION
# -------------------------
def estimate_cost(text: str):
    estimated_tokens = max(100, len(text.split()) * 10)
    estimated_cost = round((estimated_tokens / 1000) * 0.01, 4)
    return estimated_tokens, estimated_cost


# ------------------------------------------------
# CREATE EXECUTION (PLANNER IS AUTHORITATIVE)
# ------------------------------------------------
def create_execution(db: Session, user_email: str, plan: dict) -> Execution:
    """
    Creates an Execution strictly from the planner output.
    NO reinterpretation.
    """

    # ---------------- USER ----------------
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(email=user_email)
        db.add(user)
        db.commit()

    # ---------------- COST ----------------
    tokens, cost = estimate_cost(
        plan.get("params", {}).get("raw_input", "")
    )

    # ---------------- STATUS ----------------
    execution_type = plan.get("execution_type")

    if execution_type == "tracking":
        status = "active"              # 🔥 cron depends on this
    elif plan.get("requires_approval", True):
        status = "awaiting_approval"
    else:
        status = "executing"

    # ---------------- EXECUTION ----------------
    execution = Execution(
        id=plan["plan_id"],
        user_email=user_email,
        intent=plan.get("intent", "agentic_execution"),
        actions=plan.get("actions", []),
        agents=plan.get("agents", []),            # ✅ TRUST PLANNER
        params={
            **plan.get("params", {}),
            "execution_type": execution_type,
            "execution_channel": plan.get("execution_channel"),
            "agent_results": {},
            "agent_errors": {}
        },
        status=status,
        requires_approval=plan.get("requires_approval", True),
        estimated_tokens=tokens,
        estimated_cost=cost,
        xp_gained=0
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # ---------------- TIMELINE ----------------
    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message=f"Execution created ({execution.intent})"
        )
    )
    db.commit()

    return execution


# ------------------------------------------------
# APPROVE EXECUTION (RUN AGENTS)
# ------------------------------------------------
async def approve_execution(db: Session, execution: Execution):
    """
    Executes agents exactly as planner defined.
    """

    if execution.status not in ["awaiting_approval", "active"]:
        raise ValueError(
            f"Execution is in '{execution.status}' state"
        )

    execution.status = "executing"
    db.commit()

    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message="Execution approved by user"
        )
    )
    db.commit()

    # ---------------- RUN AGENTS ----------------
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
        user_input=execution.params.get("raw_input")
    )

    # ---------------- FINAL STATUS ----------------
    if execution.params.get("execution_type") == "tracking":
        execution.status = "active"     # stays active for cron
    else:
        execution.status = "executed"

    # ---------------- XP (ALWAYS AWARD) ----------------
    user = db.query(User).filter(
        User.email == execution.user_email
    ).first()

    xp_awarded = 15
    execution.xp_gained = xp_awarded

    if user:
        user.xp += xp_awarded

    db.commit()

    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message=f"XP awarded: +{xp_awarded} (Total XP: {user.xp if user else 'N/A'})"
        )
    )
    db.commit()

    return {
        "status": execution.status,
        "execution_id": execution.id,
        "result": result,
        "xp_gained": xp_awarded,
        "total_xp": user.xp if user else None,
        "estimated_tokens": execution.estimated_tokens,
        "estimated_cost": execution.estimated_cost
    }








