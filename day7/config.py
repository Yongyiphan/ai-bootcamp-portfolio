import os
from pathlib import Path

from dotenv import load_dotenv

# Load project-wide settings, followed by Day 7 settings.
DAY7_DIR = Path(__file__).resolve().parent
load_dotenv(DAY7_DIR.parent / ".env")
load_dotenv(DAY7_DIR / ".env")

# Ollama settings
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:3b")
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL)
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

# Gemini settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Shared settings
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful AI assistant.")
DB_NAME = os.getenv("DB_NAME", "chat_history.db")
