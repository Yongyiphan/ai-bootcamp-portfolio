"""Configuration for the Review Analytics application."""

import os
from pathlib import Path

from dotenv import load_dotenv


APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env")


def _setting(name: str, default: str | None = None) -> str | None:
    """Read Streamlit secrets first, then environment variables."""
    try:
        import streamlit as st

        if name in st.secrets and str(st.secrets[name]).strip():
            return str(st.secrets[name]).strip()
    except (FileNotFoundError, KeyError, RuntimeError):
        pass
    return os.getenv(name, default)


GEMINI_API_KEY = _setting("GEMINI_API_KEY")
GEMINI_MODEL = _setting("GEMINI_MODEL", "gemini-2.5-flash")

_db_setting = _setting("DB_NAME", "review_history.db")
DB_NAME = str(
    Path(_db_setting)
    if Path(_db_setting).is_absolute()
    else APP_DIR / _db_setting
)


def require_gemini_api_key() -> str:
    """Return the configured key or raise a UI-independent error."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to lab02/.env locally or "
            "to the Streamlit Community Cloud Secrets panel."
        )
    return GEMINI_API_KEY
