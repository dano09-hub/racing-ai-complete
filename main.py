from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import date, timedelta
from requests_html import HTMLSession
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

    # Run scraping directly here for simplicity
    scraped_tips = scrape_tips()

    return {
        "today_date": today.strftime("%A %d %B %Y"),
        "future_date": tomorrow.strftime("%A %d %B %Y"),
        "today_races": scraped_tips,
        "future_races": []
    }

def scrape_tips():
    tips = []
    try:
        session = HTMLSession()
        r = session.get("https://gg.co.uk/tips/today/", timeout=15)
        r.html.render(timeout=20, sleep=2)
        soup = BeautifulSoup(r.html.html, 'html.parser')

        # Example selector - adjust based on actual GG page structure
        tip_elements = soup.find_all('div', class_='tip-item')  # change this selector
        for el in tip_elements[:5]:  # limit to 5 for speed
            horse = el.find('span', class_='horse-name')
            horse_text = horse.text.strip() if horse else "Unknown Horse"
            tip_text = el.text.strip()[:100] + "..." if len(el.text) > 100 else el.text.strip()
            tips.append({
                "time": "TBD",
                "track": "Various",
                "horse": horse_text,
                "odds": "TBD",
                "ai_score": 75,
                "explanation": f"Scraped tip from GG: {tip_text}",
                "highlighted": True
            })
    except Exception as e:
        tips.append({
            "horse": "Error",
            "explanation": f"Scraping failed: {str(e)[:100]}",
            "highlighted": False
        })

    return tips

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
