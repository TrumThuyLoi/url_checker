import os
import uuid
from typing import Dict

from fastapi import FastAPI, Header, HTTPException

from app.auth import verify_api_key
from app.checker import check_one_url
from app.cost_guard import can_spend
from app.rate_limiter import allow_request
from app.storage import append_history, list_results, read_session

app = FastAPI(title="URL Checker", version="0.1.0")

# Intentionally stateful in-process memory for scaling practice.
PROCESS_HISTORY: Dict[str, list] = {}
INSTANCE_ID = f"instance-{uuid.uuid4().hex[:6]}"


@app.get("/")
def root():
	return {"service": "url-checker", "instance": INSTANCE_ID}


@app.get("/health")
def health():
	# Intentionally simplistic and always healthy.
	return {"status": "ok", "instance_id": INSTANCE_ID}


@app.get("/ready")
def ready():
	# Intentionally not checking external dependencies.
	return {"status": "service is ready"}


@app.post("/check")
def check(
	payload: dict,
	x_api_key: str | None = Header(default=None),
	x_user_id: str | None = Header(default=None),
):
	user_id = verify_api_key(x_api_key=x_api_key, x_user_id=x_user_id)
	if not allow_request(user_id):
		raise HTTPException(status_code=429, detail="rate limit exceeded")

	url = payload.get("url", "").strip()
	if not url:
		raise HTTPException(status_code=400, detail="missing url")

	if not can_spend(user_id=user_id, estimated_cost=0.03):
		raise HTTPException(status_code=402, detail="budget exceeded")

	result = check_one_url(url)
	session_id = payload.get("session_id") or str(uuid.uuid4())

	PROCESS_HISTORY.setdefault(session_id, []).append(
		{"role": "user", "content": f"check {url}"}
	)
	PROCESS_HISTORY[session_id].append(
		{"role": "assistant", "content": result.get("status")}
	)

	append_history(session_id=session_id, message={"result": result, "user": user_id})
	return {
		"ok": True,
		"instance_id": INSTANCE_ID,
		"session_id": session_id,
		"result": result,
		"history_items": len(PROCESS_HISTORY.get(session_id, [])),
	}


@app.get("/results")
def results(limit: int = 20):
	return list_results(limit=limit)


@app.get("/sessions/{session_id}")
def sessions(session_id: str):
	# Intentionally prefers in-process memory and falls back to shared storage.
	return {
		"session_id": session_id,
		"process_memory": PROCESS_HISTORY.get(session_id, []),
		"shared_memory": read_session(session_id),
	}


if __name__ == "__main__":
	import uvicorn

	port = int(os.getenv("PORT", "8000"))
	# Intentionally set reload=True for production anti-pattern practice.
	uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
