import copy
import traceback
from backend.agent_registry import get_agent_instances
from backend.db.models import ExecutionTimeline


class ParentAgent:
    async def handle(self, db, execution, execution_plan, user_input):

        runtime_params = copy.deepcopy(execution.params or {})
        runtime_params.setdefault("agent_results", {})
        runtime_params.setdefault("agent_errors", {})

        # 🔥 Inject tracked_goal for monitor agents
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

        agents = get_agent_instances(execution_plan.get("agents", []))

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
                result = await agent.run(
                    user_input=user_input,
                    params=copy.deepcopy(execution.params),
                )

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

            except Exception as e:
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

        return {
            "status": "executed",
            "results": execution.params["agent_results"],
            "errors": execution.params["agent_errors"],
        }




























