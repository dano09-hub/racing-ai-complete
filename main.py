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
        "future_races": [],
        "log": "Scraping ran - check for horses below"
    }

def scrape_tips():
    races = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://gg.co.uk/tips/today/", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Broader selectors for GG tips (2026 page structure)
        tip_blocks = soup.find_all(['div', 'article', 'li'], class_=['tip', 'tip-card', 'betting-tip', 'horse-tip'])
        if not tip_blocks:
            tip_blocks = soup.find_all(['a', 'span'], string=lambda t: t and ('horse' in t.lower() or 'tip' in t.lower()))

        for block in tip_blocks[:5]:
            horse = "Unknown Horse"
            odds = "TBD"
            # Try multiple ways to find horse name
            horse_tag = block.find(['span', 'a', 'h3'], class_=['horse-name', 'horse', 'runner-name'])
            if horse_tag:
                horse = horse_tag.text.strip()
            else:
                text = block.text.strip()
                if 'on ' in text or '@' in text:
                    horse = text.split('on ')[0] or text.split('@')[0].strip()

            races.append({
                "time": "TBD",
                "track": "GG Tips",
                "horse": horse,
                "odds": odds,
                "ai_score": 80,
                "explanation": "Live scraped tip from GG.co.uk",
                "highlighted": True
            })

        if not races:
            races.append({
                "horse": "No tips found",
                "odds": "N/A",
                "ai_score": 0,
                "explanation": "No matching tips on GG - selector may need update",
                "highlighted": False
            })
    except Exception as e:
        races.append({
            "horse": "Scraping Error",
            "odds": "N/A",
            "ai_score": 0,
            "explanation": str(e)[:150],
            "highlighted": False
        })

    return races

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
