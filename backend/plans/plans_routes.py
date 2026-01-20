from fastapi import APIRouter

router = APIRouter(
    prefix="/api/plans",
    tags=["Plans"]
)

@router.post("")
async def create_plan(plan: dict):
    print("📥 RECEIVED PLAN FROM DIFY:", plan)

    # TODO: store in DB later
    return {
        "plan_id": "plan_123",
        "status": "stored"
    }
