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
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://gg.co.uk/tips/today/", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Simple text search for horse names (works on most tip pages)
        potential = soup.find_all(string=lambda t: t and any(word in t.lower() for word in ['horse', 'runner', 'nap', 'tip', '@']))
        for text in potential[:5]:
            text = text.strip()
            if len(text) < 10:
                continue
            horse = text.split(' ')[0] + " " + text.split(' ')[1] if len(text.split()) > 1 else text[:30]
            races.append({
                "time": "TBD",
                "track": "GG Tips",
                "horse": horse,
                "odds": "TBD",
                "ai_score": 80,
                "explanation": "Live scraped from GG.co.uk",
                "highlighted": True
            })
    except Exception as e:
        races.append({
            "horse": "Error",
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
