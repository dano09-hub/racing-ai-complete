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
import random

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
        "today_races": [],  # populated after scrape
        "future_races": []
    }

@app.get("/api/scrape")
def scrape_live():
    log = ["🚀 Starting live scraping with requests-html..."]

    session = HTMLSession()

    # The Racing API
    try:
        user = os.getenv('THE_RACING_API_USER')
        pw = os.getenv('THE_RACING_API_PASS')
        if user and pw:
            r = session.get("https://api.theracingapi.com/v1/racecards/free?day=today&region_codes=gb,ire", auth=(user, pw), timeout=12)
            if r.ok:
                log.append("✅ The Racing API: racecards loaded")
            else:
                log.append(f"⚠️ The Racing API status: {r.status_code}")
        else:
            log.append("⚠️ Missing The Racing API credentials")
    except Exception as e:
        log.append(f"⚠️ The Racing API error: {str(e)[:100]}")

    # TipMeerkat
    try:
        r = session.get("https://tipmeerkat.com/latest-tips-picks", timeout=15)
        r.html.render(timeout=20, sleep=2)
        soup = BeautifulSoup(r.html.html, 'html.parser')
        log.append("✅ TipMeerkat scraped")
    except Exception as e:
        log.append(f"⚠️ TipMeerkat error: {str(e)[:100]}")

    # GG tips
    try:
        r = session.get("https://gg.co.uk/tips/today/", timeout=15)
        r.html.render(timeout=20, sleep=2)
        log.append("✅ GG tips scraped")
    except Exception as e:
        log.append(f"⚠️ GG error: {str(e)[:100]}")

    log.append("✅ All scraping finished")

    return {"status": "success", "message": "\n".join(log)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
