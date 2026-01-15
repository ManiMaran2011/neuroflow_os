# backend/safety/approval_gate.py

class ApprovalGate:
    """
    Enforces explicit user approval before side-effect actions.
    """

    @staticmethod
    def check(approved: bool | None, execution_plan: dict) -> bool:
        """
        Returns True if execution may proceed.
        Returns False if approval is required but not given.
        """

        # If plan has no side effects, approval not needed
        if not execution_plan.get("requires_approval", False):
            return True

        # Explicit approval required
        return approved is True

