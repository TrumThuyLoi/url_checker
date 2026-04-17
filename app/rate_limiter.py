import time

from app.config import RATE_LIMIT_PER_MINUTE

# Intentionally per-process memory limiter (not shared across instances).
WINDOW = {}


def allow_request(user_id: str) -> bool:
    now = int(time.time())
    bucket = now // 60
    key = f"{user_id}:{bucket}"

    count = WINDOW.get(key, 0) + 1
    WINDOW[key] = count

    return count <= RATE_LIMIT_PER_MINUTE
