import os
from pathlib import Path

from dotenv import load_dotenv

# Load project-wide settings, followed by Day 7 settings.
DAY7_DIR = Path(__file__).resolve().parent
load_dotenv(DAY7_DIR.parent / ".env")
load_dotenv(DAY7_DIR / ".env")

def get_setting(name, default=None):
    """Read Streamlit Cloud secrets first, then environment/.env values."""
    try:
        import streamlit as st

        if name in st.secrets:
            value = st.secrets[name]
            if value is not None and str(value).strip():
                return str(value).strip()
    except Exception:
        # No Streamlit runtime or secrets file is expected for CLI/local usage.
        pass

    value = os.getenv(name)
    if value and value.strip():
        return value.strip()

    return default


# Ollama settings
DEFAULT_PROVIDER = get_setting("DEFAULT_PROVIDER", "ollama").lower()
DEFAULT_MODEL = get_setting("DEFAULT_MODEL", "llama3.2:3b")
MODEL_NAME = get_setting("MODEL_NAME", DEFAULT_MODEL)
OLLAMA_API_BASE = get_setting("OLLAMA_API_BASE", "http://localhost:11434")

# Gemini settings
GEMINI_API_KEY = get_setting("GEMINI_API_KEY")
GEMINI_MODEL = get_setting("GEMINI_MODEL", "gemini-3.5-flash")

# Shared settings
SYSTEM_PROMPT = get_setting("SYSTEM_PROMPT", "You are a helpful AI assistant.")
DB_NAME = get_setting("DB_NAME", "chat_history.db")
