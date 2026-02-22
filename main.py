# main.py
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

app = FastAPI(title="Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapeResponse(BaseModel):
    success: bool
    url: str
    title: str | None = None
    content_snippet: str | None = None
    error: str | None = None
    timestamp: str


@app.get("/api/today")
async def get_today():
    now = datetime.utcnow()
    return {"today": now.strftime("%Y-%m-%d"), "utc_datetime": now.isoformat()}


@app.get("/api/scrape", response_model=ScrapeResponse)
@app.get("/api/scrape/{url:path}", response_model=ScrapeResponse)
async def scrape_url(url: str | None = None):
    if not url:
        raise HTTPException(status_code=400, detail="Missing ?url= parameter")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = {
        "success": False,
        "url": url,
        "title": None,
        "content_snippet": None,
        "error": None,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )

            await page.goto(url, wait_until="domcontentloaded", timeout=45000)

            title = await page.title()
            result["title"] = title.strip() if title else None

            # Extract main content
            content = ""
            for sel in ["article", "main", ".content", "#content", ".post-body"]:
                elem = page.locator(sel).first
                if await elem.is_visible():
                    content = await elem.inner_text()
                    break
            if not content:
                content = await page.inner_text("body")

            content = " ".join(content.split())
            result["content_snippet"] = content[:500] + ("..." if len(content) > 500 else "")
            result["success"] = True

            await browser.close()
    except Exception as e:
        result["error"] = str(e)

    return result


@app.get("/")
async def root():
    return {"message": "API running", "scrape_example": "/api/scrape?url=https://example.com"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
