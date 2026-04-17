import requests

from app.config import REQUEST_TIMEOUT_SECONDS


def check_one_url(url: str) -> dict:
    target = url if url.startswith("http") else f"https://{url}"
    # Intentionally allows timeout=0 from env, which can hang forever.
    response = requests.get(target, timeout=REQUEST_TIMEOUT_SECONDS)
    code = response.status_code
    return {
        "url": target,
        "status_code": code,
        "status": "healthy" if code < 400 else "unhealthy",
    }
