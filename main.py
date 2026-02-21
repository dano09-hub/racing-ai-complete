from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
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
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://gg.co.uk/tips/today/", timeout=60000)
            page.wait_for_load_state("networkidle")
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # 2026 GG tip selector (broad match)
            tip_blocks = soup.find_all(['div', 'article'], attrs={"class": lambda x: x and ('tip' in x.lower() or 'bet' in x.lower() or 'selection' in x.lower())})
            for block in tip_blocks[:5]:
                horse = block.find(['span', 'a'], string=lambda t: t and 'horse' in t.lower())
                horse_text = horse.text.strip() if horse else "Unknown Horse"
                races.append({
                    "time": "TBD",
                    "track": "GG Tips",
                    "horse": horse_text,
                    "odds": "TBD",
                    "ai_score": 80,
                    "explanation": "Live scraped with Playwright from GG.co.uk",
                    "highlighted": True
                })
            browser.close()
    except Exception as e:
        races.append({
            "horse": "Scraping Error",
            "explanation": str(e)[:150],
            "highlighted": False
        })
    return races

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
