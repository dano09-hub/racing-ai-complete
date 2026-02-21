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

    scraped = scrape_tips()

    return {
        "today_date": today.strftime("%A %d %B %Y"),
        "future_date": tomorrow.strftime("%A %d %B %Y"),
        "today_races": scraped,
        "future_races": []
    }

def scrape_tips():
    races = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://gg.co.uk/tips/today/", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # GG tip selector (adjust if page changes)
        tip_blocks = soup.find_all('div', class_='tip-card')  # common class for tips
        for block in tip_blocks[:5]:  # limit to 5
            horse_tag = block.find('span', class_='horse-name') or block.find('a', class_='horse')
            horse = horse_tag.text.strip() if horse_tag else "Unknown Horse"
            odds_tag = block.find('span', class_='odds')
            odds = odds_tag.text.strip() if odds_tag else "TBD"
            races.append({
                "time": "TBD",
                "track": "Various",
                "horse": horse,
                "odds": odds,
                "ai_score": 80,
                "explanation": "Scraped tip from GG.co.uk",
                "highlighted": True
            })
    except Exception as e:
        races.append({
            "horse": "Scraping Error",
            "odds": "N/A",
            "ai_score": 0,
            "explanation": str(e)[:100],
            "highlighted": False
        })

    return races

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
