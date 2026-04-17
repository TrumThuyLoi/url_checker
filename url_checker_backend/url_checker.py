import os
import json
from pathlib import Path
from typing import List, Dict

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent
URLS_FILE = BASE_DIR / "urls.txt"
RESULTS_FILE = BASE_DIR / "url_check_results.json"

app = FastAPI(title="URL Checker API", version="1.0.0")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed_origins.split(",")] if allowed_origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

def check_urls() -> List[Dict]:
    if not URLS_FILE.exists():
        raise HTTPException(status_code=500, detail=f"{URLS_FILE.name} not found")

    with URLS_FILE.open("r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    results = []
    for url in urls:
        target = url if url.startswith("http") else f"https://{url}"
        try:
            response = requests.get(target, timeout=5)
            code = response.status_code
            status = "healthy" if code < 400 else "unhealthy"
            results.append({"url": target, "status": status, "status_code": code})
        except requests.RequestException:
            results.append({"url": target, "status": "unreachable", "status_code": None})

    with RESULTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

@app.get("/")
def root():
    return {"message": "URL Checker API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/results")
def get_results():
    if not RESULTS_FILE.exists():
        return []
    with RESULTS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/check")
def run_check():
    results = check_urls()
    return {"message": "Done", "total": len(results), "results": results}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("url_checker:app", host="0.0.0.0", port=port, reload=False)