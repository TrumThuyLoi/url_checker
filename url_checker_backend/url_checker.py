# url_checker.py
import requests
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_urls():
    with open("urls.txt", "r") as f:
        urls = [line.strip() for line in f]

    results = []
    for url in urls:
        try:
            if not url.startswith("http"):
                url = "https://" + url
            response = requests.get(url, timeout=5)
            code = response.status_code
            status = "healthy" if code < 400 else "unhealthy"
            results.append({"url": url, "status": status, "status_code": code})
        except:
            results.append({"url": url, "status": "unreachable", "status_code": None})

    with open("url_check_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


@app.get("/results")      
def get_results():
    with open("url_check_results.json") as f:
        return json.load(f)

@app.post("/check")       
def run_check():
    results = check_urls()
    return {"message": "Done", "total": len(results)}