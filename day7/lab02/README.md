# Lab 02 — Review Analytics Platform

This project refactors the provided single-file application into four layers:

- `config.py` — environment and Streamlit Cloud configuration
- `database/db_manager.py` — all SQLite persistence
- `services/gemini_service.py` — Gemini analysis and rating parsing
- `app.py` — Streamlit interface and navigation only

## Run locally

```powershell
cd day7\lab02
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m streamlit run app.py
```

Replace the placeholder in `.env` with your Gemini API key. Test the app by
uploading `good.txt` and `bad.txt`; their results should be routed to the Good
and Bad history categories respectively.

## Deploy

Deploy `day7/lab02/app.py` on Streamlit Community Cloud. Add the following in
the app's **Settings → Secrets** panel:

```toml
GEMINI_API_KEY = "your-key"
GEMINI_MODEL = "gemini-2.5-flash"
DB_NAME = "review_history.db"
```

Do not commit `.env`, `review_history.db`, API keys, or Python cache files.
The included `.gitignore` excludes these local-only files. For Streamlit Cloud,
enter the secrets manually in **Settings → Secrets**; no secret belongs in the
repository or in `requirements.txt`.
