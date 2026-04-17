import json
import os
from pathlib import Path
from typing import Any

# Store runtime data in a writable directory instead of the source tree.
DATA_DIR = Path(os.getenv("DATA_DIR", "/tmp/url_checker"))
RESULTS_FILE = DATA_DIR / "url_check_results.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_all() -> list[dict[str, Any]]:
    if not RESULTS_FILE.exists():
        return []
    with RESULTS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_all(rows: list[dict[str, Any]]) -> None:
    _ensure_data_dir()
    with RESULTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def append_history(session_id: str, message: dict[str, Any]) -> None:
    data = _read_all()
    data.append({"session_id": session_id, "message": message})
    _write_all(data)


def list_results(limit: int = 20) -> list[dict[str, Any]]:
    return _read_all()[-limit:]


def read_session(session_id: str) -> list[dict[str, Any]]:
    return [row for row in _read_all() if row.get("session_id") == session_id]
