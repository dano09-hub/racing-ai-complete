from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
from requests_html import HTMLSession

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

    # Run scraping here for simplicity (in production, run it separately/cron)
    scraped_data = scrape_data()

    return {
        "today_date": today.strftime("%A %d %B %Y"),
        "future_date": tomorrow.strftime("%A %d %B %Y"),
        "today_races": scraped_data["today_races"],
        "future_races": []
    }

def scrape_data():
    log = []
    today_races = []

    session = HTMLSession()

    # Example scraping - replace with your full sites
    try:
        r = session.get("https://gg.co.uk/tips/today/", timeout=15)
        r.html.render(timeout=20, sleep=2)
        soup = BeautifulSoup(r.html.html, 'html.parser')
        tips = soup.find_all('div', class_='tip')  # adjust selector
        for tip in tips[:3]:  # limit for demo
            horse = tip.find('span', class_='horse').text if tip.find('span', class_='horse') else "Unknown"
            today_races.append({
                "time": "14:30",
                "track": "Ascot",
                "horse": horse,
                "odds": "5.0",
                "ai_score": 85,
                "explanation": "Scraped tip from GG",
                "highlighted": True
            })
        log.append("✅ GG tips scraped")
    except Exception as e:
        log.append(f"⚠️ Scraping error: {str(e)}")

    return {"today_races": today_races, "log": log}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
