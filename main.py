from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
app = FastAPI(title="Racing AI")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html") as f: return f.read()
print("✅ API ready - open in browser")
