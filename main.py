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
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        
        # TipMeerkat (easier to scrape, public tips)
        r = requests.get("https://tipmeerkat.com/latest-tips-picks", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # TipMeerkat selector - look for horse/tip patterns
        tip_blocks = soup.find_all(['div', 'p', 'span'], string=lambda t: t and any(word in t.lower() for word in ['horse', 'runner', 'tip', 'nap', '@', 'odds']))
        for el in tip_blocks[:5]:
            text = el.text.strip()
            if len(text) < 10:
                continue
            horse = text.split(' ')[0] + " " + text.split(' ')[1] if len(text.split()) > 1 else text[:30]
            races.append({
                "time": "TBD",
                "track": "TipMeerkat",
                "horse": horse,
                "odds": "TBD",
                "ai_score": 80,
                "explanation": "Live scraped tip from TipMeerkat",
                "highlighted": True
            })

        if not races:
            # Fallback to GG
            r = requests.get("https://gg.co.uk/tips/today/", headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            tip_blocks = soup.find_all(['div', 'p', 'span'], string=lambda t: t and 'horse' in t.lower())
            for el in tip_blocks[:3]:
                horse = el.text.strip()[:30]
                races.append({
                    "time": "TBD",
                    "track": "GG Tips",
                    "horse": horse,
                    "odds": "TBD",
                    "ai_score": 75,
                    "explanation": "Fallback scraped from GG",
                    "highlighted": False
                })

        if not races:
            races.append({
                "horse": "No tips found",
                "odds": "N/A",
                "ai_score": 0,
                "explanation": "No matching patterns on TipMeerkat or GG - sites may be JS-heavy (2026 version)",
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
