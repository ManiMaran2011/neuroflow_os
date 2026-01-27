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
# AGENT INJECTION LOGIC
# ------------------------------------------------
def resolve_agents(plan: dict) -> list[str]:
    """
    Decide which agents should execute.
    Planner NEVER decides agents.
    """

    execution_type = plan.get("execution_type")
    channel = plan.get("execution_channel")

    # ---- TRACKED / HABIT / FITNESS ----
    if execution_type in ["tracked_goal", "tracking"]:
        return [
            "MonitorAgent",       # real (daily cron tracking)
            "ReportAgent",
            "XPAgent"
        ]

    # ---- ONE-TIME TASK ----
    if execution_type == "instant_task":
        if channel == "calendar":
            return ["CalendarAgent", "XPAgent", "ReportAgent"]
        if channel == "email":
            return ["NotifyAgent", "XPAgent", "ReportAgent"]

    # ---- FALLBACK ----
    return ["ReportAgent", "XPAgent"]


# ------------------------------------------------
# CREATE EXECUTION (🔥 FIXED)
# ------------------------------------------------
def create_execution(db: Session, user_email: str, plan: dict) -> Execution:
    # ---------------- USER ----------------
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(email=user_email)
        db.add(user)
        db.commit()

    # ---------------- COST ----------------
    tokens, cost = estimate_cost(
        plan.get("reasoning", plan.get("params", {}).get("raw_input", ""))
    )

    # ---------------- AGENTS ----------------
    agents = resolve_agents(plan)

    # ---------------- ACTIONS ----------------
    actions = plan.get("actions", [])
    if not actions:
        channel = plan.get("execution_channel")
        actions = [channel] if channel else []

    # ---------------- PARAMS ----------------
    params = plan.get("params", {}).copy()
    params.setdefault("agent_results", {})
    params.setdefault("agent_errors", {})

    # 🔥 CRITICAL FIX
    is_tracking = plan.get("execution_type") in ["tracked_goal", "tracking"]

    if is_tracking:
        params["execution_type"] = "tracking"   # MUST MATCH CRON FILTER
        params.setdefault("last_completed", None)
    else:
        params["execution_type"] = plan.get("execution_type")

    params["schedule"] = plan.get("schedule")

    # ---------------- EXECUTION ----------------
    requires_approval = plan.get("requires_approval", True)

    execution = Execution(
        id=plan["plan_id"],
        user_email=user_email,
        intent=plan.get("intent", "agentic_execution"),
        actions=actions,
        agents=agents,
        params=params,
        requires_approval=requires_approval,
        status="active" if is_tracking else (
            "awaiting_approval" if requires_approval else "created"
        ),
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
            message=(
                "Tracking execution activated"
                if is_tracking
                else f"Execution created (Est. cost: ${cost})"
            )
        )
    )
    db.commit()

    return execution


# ------------------------------------------------
# APPROVE EXECUTION
# ------------------------------------------------
async def approve_execution(db: Session, execution: Execution):
    if execution.status != "awaiting_approval":
        raise ValueError(f"Execution is in '{execution.status}' state")

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
        user_input=execution.params.get("raw_input")
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






