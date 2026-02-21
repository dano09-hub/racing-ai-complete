from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import time

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
    with open("static/index.html") as f:
        return f.read()

@app.get("/api/today")
def get_today():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    return {
        "today_date": today.strftime("%A %d %B %Y"),
        "future_date": tomorrow.strftime("%A %d %B %Y"),
        "today_races": [],  # populated by scrape
        "future_races": []
    }

@app.get("/api/scrape")
def scrape_live():
    log = ["🚀 Starting scraping with requests-html..."]

    session = HTMLSession()

    # Example: The Racing API (use your keys from env)
    try:
        user = os.getenv('THE_RACING_API_USER')
        pw = os.getenv('THE_RACING_API_PASS')
        if user and pw:
            r = requests.get("https://api.theracingapi.com/v1/racecards/free?day=today&region_codes=gb,ire", auth=(user, pw), timeout=12)
            if r.ok:
                log.append("✅ The Racing API: racecards loaded")
    except:
        log.append("⚠️ The Racing API failed")

    # TipMeerkat example
    try:
        r = session.get("https://tipmeerkat.com/latest-tips-picks")
        r.html.render(timeout=15, sleep=2)  # renders JS
        soup = BeautifulSoup(r.html.html, 'html.parser')
        log.append("✅ TipMeerkat scraped")
    except Exception as e:
        log.append(f"⚠️ TipMeerkat failed: {str(e)[:80]}")

    # Add more sites (GG, OLBG, etc.) the same way

    log.append("✅ Scraping complete")

    return {"status": "success", "message": "\n".join(log)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
