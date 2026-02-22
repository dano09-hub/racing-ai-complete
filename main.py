from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup

load_dotenv()

print("Loaded HEADLESS_BROWSER_URL:", os.getenv('HEADLESS_BROWSER_URL'))

app = FastAPI(title="Racing AI")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("static/index.html") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>index.html not found</h1>"

@app.get("/api/today")
def get_today():
    today = date.today()
    tomorrow = today + timedelta(days=1)

    scraped = scrape_tips()

    return {
        "today_date": today.strftime("%A %d %B %Y"),
        "future_date": tomorrow.strftime("%A %d %B %Y"),
        "today_races": scraped,
        "future_races": [],
        "log": "Scraping completed via headless browser"
    }

@app.get("/api/scrape")
def scrape_live():
    scraped = scrape_tips()
    return {
        "status": "success",
        "message": "Scraping completed via headless browser",
        "races": scraped
    }

def scrape_tips():
    races = []
    headless_url = os.getenv('HEADLESS_BROWSER_URL')

    if not headless_url:
        races.append({
            "horse": "Config Error",
            "explanation": "HEADLESS_BROWSER_URL variable is missing",
            "highlighted": False
        })
        return races

    try:
        payload = {
            "url": "https://gg.co.uk/tips/today/",
            "instructions": "Extract all horse names, odds, times, tracks, and explanations. Return as JSON list of objects with keys: horse, odds, time, track, explanation."
        }
        r = requests.post(f"{headless_url}/scrape", json=payload, timeout=40)

        if r.ok:
            result = r.json()
            for item in result.get("results", [])[:8]:
                races.append({
                    "time": item.get("time", "TBD"),
                    "track": item.get("track", "Various"),
                    "horse": item.get("horse", "Unknown"),
                    "odds": item.get("odds", "TBD"),
                    "ai_score": 80,
                    "explanation": item.get("explanation", "Scraped via headless browser"),
                    "highlighted": len(races) < 3
                })
        else:
            races.append({
                "horse": "Headless Error",
                "explanation": f"Status {r.status_code} - {r.text[:100]}",
                "highlighted": False
            })
    except Exception as e:
        races.append({
            "horse": "Connection Error",
            "explanation": str(e)[:150],
            "highlighted": False
        })

    if not races:
        races.append({
            "horse": "No tips found",
            "explanation": "Headless service returned no data",
            "highlighted": False
        })

    return races

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
