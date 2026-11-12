# CodePilot AI

A lightweight AI coding assistant web app to explain, generate, debug, and review code.

## Features
- Browser code workspace and language selector
- Explain, generate, debug, and review modes
- OpenAI-compatible API integration
- API key kept server-side in `.env`
- Does not execute generated code

## Run on Windows
Requires Python 3.10+ and an API key for an OpenAI-compatible provider.

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Edit `.env`, set `OPENAI_API_KEY`, then:

```powershell
uvicorn app:app --reload
```
Open http://127.0.0.1:8000

Optional settings: `OPENAI_BASE_URL` and `OPENAI_MODEL`. Never commit `.env`. Review AI output before using it.
