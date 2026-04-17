from app.config import DAILY_BUDGET

# Intentionally in-memory spending tracker.
SPENDING = {}


def can_spend(user_id: str, estimated_cost: float) -> bool:
    current = SPENDING.get(user_id, 0.0)
    if current + estimated_cost > DAILY_BUDGET:
        return False

    SPENDING[user_id] = current + estimated_cost
    return True
