from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import date, timedelta

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

    # Real data would come from your DB here
    # (fetch_daily_info.py populates the DB every morning)
    return {
        "today_date": today.strftime("%A %d %B %Y"),
        "future_date": tomorrow.strftime("%A %d %B %Y"),
        "today_races": [
            {
                "time": "14:30 Ascot",
                "track": "Ascot • Soft",
                "horse": "Golden Arrow",
                "odds": 4.2,
                "ai_score": 89,
                "explanation": "🎯 Trainer single-runner + 🕶️ First-time headgear + 🏁 Low draw on soft + 9/11 tipsters (TipMeerkat favourite) = 41% edge",
                "highlighted": True
            },
            # ... more real entries from DB would go here
        ],
        "future_races": [
            {
                "time": "13:45 Newmarket",
                "track": "Newmarket • Good",
                "horse": "Midnight Express",
                "odds": 12.0,
                "ai_score": 82,
                "explanation": "💎 Short price in weak field + ⭐ Class standout",
                "highlighted": True
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
