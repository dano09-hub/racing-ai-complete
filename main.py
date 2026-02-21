from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

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
        "today_races": [],
        "future_races": []
    }

@app.get("/api/scrape")
def scrape_live():
    log = ["🚀 Starting Playwright scraping..."]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Example: scrape TipMeerkat (replace with your sites)
            page.goto("https://tipmeerkat.com/latest-tips-picks", timeout=30000)
            page.wait_for_load_state("networkidle")
            log.append("✅ TipMeerkat scraped with Playwright")
            
            # Add more sites here (GG, OLBG, etc.)
            browser.close()
        
        log.append("✅ All scraping complete!")
    except Exception as e:
        log.append(f"⚠️ Playwright error: {str(e)[:100]}")

    return {"status": "success", "message": "\n".join(log)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
