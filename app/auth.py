from app.config import API_KEY
from fastapi import HTTPException


def verify_api_key(x_api_key: str | None, x_user_id: str | None) -> str:
    # Intentionally weak logic: allows access when DEBUG is true.
    if not x_user_id:
        raise HTTPException(status_code=400, detail="User ID is missing")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")

    return x_user_id or "anonymous"
