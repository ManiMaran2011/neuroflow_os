import copy
import traceback

from backend.agent_registry import get_agent_instances
from backend.db.models import ExecutionTimeline


class ParentAgent:
    """
    OS-level orchestrator.
    - Executes root agents
    - Collects results
    - Dispatches real-world actions (email / calendar / etc)
    """

    async def handle(self, db, execution, execution_plan, user_input):
        # --------------------------------------------------
        # 1️⃣ INIT RUNTIME STATE (SAFE, IMMUTABLE STYLE)
        # --------------------------------------------------
        runtime_params = copy.deepcopy(execution.params or {})
        runtime_params.setdefault("agent_results", {})
        runtime_params.setdefault("agent_errors", {})

        # 🔥 Inject tracked goal for monitoring agents
        if "tracked_goal" in execution_plan:
            runtime_params["tracked_goal"] = execution_plan["tracked_goal"]

        execution.params = runtime_params
        db.commit()

        db.add(
            ExecutionTimeline(
                execution_id=execution.id,
                message="ParentAgent started execution",
            )
        )
        db.commit()

        # --------------------------------------------------
        # 2️⃣ LOAD ROOT AGENTS
        # --------------------------------------------------
        agents = get_agent_instances(execution_plan.get("agents", []))

        # --------------------------------------------------
        # 3️⃣ EXECUTE AGENTS
        # --------------------------------------------------
        for agent in agents:
            agent_name = agent.__class__.__name__

            db.add(
                ExecutionTimeline(
                    execution_id=execution.id,
                    message=f"{agent_name} started",
                )
            )
            db.commit()

            try:
                # ---------------- RUN AGENT ----------------
                result = await agent.run(
                    user_input=user_input,
                    params=copy.deepcopy(execution.params),
                )

                # ---------------- STORE RESULT ----------------
                params = copy.deepcopy(execution.params)
                params["agent_results"][agent_name] = result
                execution.params = params
                db.commit()

                db.add(
                    ExecutionTimeline(
                        execution_id=execution.id,
                        message=f"{agent_name} completed",
                    )
                )
                db.commit()

                # --------------------------------------------------
                # 4️⃣ 🔥 REAL-WORLD ACTION DISPATCH
                # --------------------------------------------------
                if isinstance(result, dict) and result.get("action_needed"):
                    channel = result.get("execution_channel")

                    # ---------- EMAIL ----------
                    if channel == "email":
                        notify_agent = get_agent_instances(["NotifyAgent"])[0]

                        await notify_agent.run(
                            user_input="Progress check-in",
                            params={
                                # ⚠️ MUST EXIST OR FETCH FROM USER TABLE
                                "user_email": execution.user_email,
                                "message": result.get("suggested_action"),
                                "reason": result.get("reason"),
                            },
                        )

                        db.add(
                            ExecutionTimeline(
                                execution_id=execution.id,
                                message="NotifyAgent dispatched (email)",
                            )
                        )
                        db.commit()

                    # ---------- CALENDAR (stub) ----------
                    elif channel == "calendar":
                        calendar_agent = get_agent_instances(["CalendarAgent"])[0]

                        await calendar_agent.run(
                            user_input="Schedule progress check-in",
                            params={
                                "title": "Progress Check-in",
                                "notes": result.get("reason"),
                            },
                        )

                        db.add(
                            ExecutionTimeline(
                                execution_id=execution.id,
                                message="CalendarAgent dispatched",
                            )
                        )
                        db.commit()

            except Exception as e:
                # ---------------- ERROR HANDLING ----------------
                params = copy.deepcopy(execution.params)
                params["agent_errors"][agent_name] = {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
                execution.params = params
                db.commit()

                db.add(
                    ExecutionTimeline(
                        execution_id=execution.id,
                        message=f"{agent_name} failed",
                    )
                )
                db.commit()

        # --------------------------------------------------
        # 5️⃣ FINAL RESPONSE
        # --------------------------------------------------
        return {
            "status": "executed",
            "results": execution.params.get("agent_results", {}),
            "errors": execution.params.get("agent_errors", {}),
        }




























