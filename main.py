# main.py
import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Optional: if you're really using RSS from Racing Post
try:
    import feedparser
except ImportError:
    feedparser = None
    logging.warning("feedparser not installed - RSS features will be disabled")

# Playwright - async version
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

app = FastAPI(
    title="Scraper API",
    description="Simple scraping & today endpoint",
    version="0.1.0"
)

# Allow frontend (adjust origins in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # ← tighten this in prod!
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


@app.get("/api/today", response_model=dict)
async def get_today():
    """Simple endpoint that returns current date/time"""
    now = datetime.utcnow()
    return {
        "today": now.strftime("%Y-%m-%d"),
        "utc_datetime": now.isoformat(),
        "message": "Hello from today endpoint"
    }


@app.get("/api/scrape", response_model=ScrapeResponse)
@app.get("/api/scrape/{url:path}", response_model=ScrapeResponse)
async def scrape_url(url: str | None = None):
    """
    Scrape a webpage using Playwright (headless Chromium).
    Example: /api/scrape?url=https://example.com
    """
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
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                viewport={"width": 1280, "height": 800},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            except PlaywrightTimeout:
                result["error"] = "Timeout while loading page"
                await browser.close()
                return result

            try:
                title = await page.title()
                result["title"] = title.strip() if title else None
            except Exception:
                result["title"] = None

            # Example selectors —
