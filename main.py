from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup

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

    scraped = scrape_data()

    return {
        "today_date": today.strftime("%A %d %B %Y"),
        "future_date": tomorrow.strftime("%A %d %B %Y"),
        "today_races": scraped["races"],
        "future_races": [],
        "log": scraped["log"]
    }

def scrape_data():
    log = ["Starting scraping..."]
    races = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Example: scrape GG tips (adjust selector for real page)
    try:
        r = requests.get("https://gg.co.uk/tips/today/", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        tip_blocks = soup.find_all('div', class_='tip')  # change to actual class
        for block in tip_blocks[:3]:  # limit for speed
            horse_tag = block.find('span', class_='horse-name')
            horse = horse_tag.text.strip() if horse_tag else "Unknown Horse"
            races.append({
                "time": "TBD",
                "track": "Various",
                "horse": horse,
                "odds": "TBD",
                "ai_score": 75,
                "explanation": "Scraped tip from GG",
                "highlighted": True
            })
        log.append("✅ GG tips scraped")
    except Exception as e:
        log.append(f"⚠️ GG scraping failed: {str(e)[:100]}")

    # Add more sites here (TipMeerkat, OLBG, etc.) the same way

    log.append("Scraping finished")
    return {"races": races, "log": log}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
