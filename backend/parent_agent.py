from backend.agent_registry import get_agent_instances
from backend.db.models import ExecutionTimeline
import traceback
import copy


class ParentAgent:
    async def handle(self, db, execution, execution_plan, user_input):

        # ---------------- INIT RUNTIME STATE (SAFE) ----------------
        base_params = execution.params or {}

        # 🔥 IMPORTANT: create a NEW dict (not mutate in-place)
        runtime_params = copy.deepcopy(base_params)

        runtime_params["agent_results"] = {}
        runtime_params["agent_errors"] = {}

        execution.params = runtime_params
        db.commit()

        db.add(
            ExecutionTimeline(
                execution_id=execution.id,
                message="ParentAgent started execution"
            )
        )
        db.commit()

        agents = get_agent_instances(execution_plan.get("agents", []))

        for agent in agents:
            agent_name = agent.__class__.__name__

            db.add(
                ExecutionTimeline(
                    execution_id=execution.id,
                    message=f"{agent_name} execution started"
                )
            )
            db.commit()

            try:
                result = await agent.run(
                    user_input=user_input,
                    params=execution_plan.get("params", {})
                )

                # 🔥 REASSIGN JSON (critical)
                params = copy.deepcopy(execution.params)
                params["agent_results"][agent_name] = result
                execution.params = params
                db.commit()

                db.add(
                    ExecutionTimeline(
                        execution_id=execution.id,
                        message=f"{agent_name} execution completed"
                    )
                )
                db.commit()

            except Exception as e:
                error_result = {
                    "status": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }

                params = copy.deepcopy(execution.params)
                params["agent_errors"][agent_name] = error_result
                execution.params = params
                db.commit()

                db.add(
                    ExecutionTimeline(
                        execution_id=execution.id,
                        message=f"{agent_name} execution failed"
                    )
                )
                db.commit()

        return {
            "status": "executed",
            "results": execution.params.get("agent_results", {}),
            "errors": execution.params.get("agent_errors", {})
        }



























