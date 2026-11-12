import os
from pathlib import Path
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()
app = FastAPI(title="CodePilot AI", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

class AssistRequest(BaseModel):
    mode: str = Field(pattern="^(explain|generate|debug|review)$")
    language: str = Field(default="Python", max_length=40)
    prompt: str = Field(min_length=3, max_length=12000)
    code: str = Field(default="", max_length=30000)

@app.get("/", response_class=HTMLResponse)
async def home():
    return Path("static/index.html").read_text(encoding="utf-8")

@app.get("/api/health")
async def health():
    return {"status": "ok", "configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/api/assist")
async def assist(req: AssistRequest):
    key = os.getenv("OPENAI_API_KEY")
    if not key or key == "replace_me":
        raise HTTPException(503, "Add your API key to .env, then restart CodePilot.")
    instructions = {
        "explain": "Explain the supplied code clearly, including purpose and important parts.",
        "generate": "Generate readable code for the requested task and include brief usage notes.",
        "debug": "Find likely bugs, explain their causes, and provide corrected code.",
        "review": "Review correctness, readability, performance, and security. Prioritize actionable findings."
    }
    content = f"Language: {req.language}\nTask: {req.prompt}\n\nCode:\n{req.code or '(No code supplied)'}"
    url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
    payload = {"model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"), "messages": [
        {"role": "system", "content": instructions[req.mode] + " Do not claim you executed code."},
        {"role": "user", "content": content}], "temperature": 0.2}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, headers={"Authorization": f"Bearer {key}"}, json=payload)
            response.raise_for_status()
            data = response.json()
            return {"answer": data["choices"][0]["message"]["content"], "model": payload["model"]}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"AI provider returned {exc.response.status_code}: {exc.response.text[:1000]}")
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(502, f"AI request failed: {exc}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
