"""Context-aware chatbot with persistent, retrieved memory."""

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from groq import Groq


BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "chat_memory.db"
SKILLS_FILE = BASE_DIR / "skills.md"
MEMORY_SEED_FILE = BASE_DIR / "memory_seed.json"
MODEL = "llama-3.1-8b-instant"
USER_ID = "user_01"
RECENT_MESSAGE_LIMIT = 6
RELEVANT_MEMORY_LIMIT = 6

load_dotenv(BASE_DIR / ".env")

# Common words do not help a simple keyword search find useful memories.
STOP_WORDS = {
    "about", "after", "again", "also", "and", "are", "can", "could",
    "does", "for", "from", "have", "how", "into", "just", "like",
    "that", "the", "their", "then", "there", "they", "this", "was",
    "what", "when", "where", "which", "who", "why", "will", "with",
    "would", "your",
}


def connect_db():
    """Open a short-lived connection that is safe to use from Gradio threads."""
    return sqlite3.connect(DATABASE_FILE)


def setup_database():
    with connect_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id, id)"
        )


def load_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def load_seed_memory():
    try:
        return json.loads(MEMORY_SEED_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def format_seed_memory(seed):
    lines = []
    for item in seed.get("past_interactions", []):
        lines.append(
            f'- {item.get("date", "Unknown date")} | '
            f'{item.get("topic", "General")}: {item.get("summary", "")}'
        )
    lines.extend(f"- {fact}" for fact in seed.get("saved_facts", []))
    return "\n".join(lines) or "No seed memory is available."


def save_memory(role, content, user_id=USER_ID):
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect_db() as connection:
        connection.execute(
            "INSERT INTO messages (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, role, content, timestamp),
        )


def get_recent_history(user_id=USER_ID, limit=RECENT_MESSAGE_LIMIT):
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT role, content FROM messages
            WHERE user_id = ? ORDER BY id DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [
        {"role": role, "content": content}
        for role, content in reversed(rows)
    ]


def extract_keywords(text):
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    return list(dict.fromkeys(
        word for word in words if len(word) > 3 and word not in STOP_WORDS
    ))[:10]


def search_memory(prompt, user_id=USER_ID, limit=RELEVANT_MEMORY_LIMIT):
    """Return older messages matching useful words in the current prompt."""
    keywords = extract_keywords(prompt)
    if not keywords:
        return []

    conditions = " OR ".join("LOWER(content) LIKE ?" for _ in keywords)
    parameters = [user_id, *[f"%{word}%" for word in keywords], limit]
    query = f"""
        SELECT role, content, timestamp FROM messages
        WHERE user_id = ? AND ({conditions})
        ORDER BY id DESC LIMIT ?
    """
    with connect_db() as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [
        {"role": role, "content": content, "timestamp": timestamp}
        for role, content, timestamp in rows
    ]


def format_relevant_memory(memories):
    if not memories:
        return "No matching conversation memory was found."
    return "\n".join(
        f'- [{item["timestamp"]}] {item["role"]}: {item["content"]}'
        for item in memories
    )


def build_messages(prompt, user_id=USER_ID):
    profile = load_text(SKILLS_FILE) or "No learner profile is available."
    seed_memory = format_seed_memory(load_seed_memory())
    relevant_memory = format_relevant_memory(search_memory(prompt, user_id))
    system_prompt = f"""You are a helpful learning assistant for an AI learner.

Use the learner profile, seed memory, retrieved conversation memory, and recent
chat only when they are relevant. Never invent personal facts. If the user asks
for a personal fact that is not present in the supplied context, say "I don't
know". Prefer simple explanations, step-by-step examples, and short code demos.

LEARNER PROFILE:
{profile}

SEED MEMORY:
{seed_memory}

RETRIEVED CONVERSATION MEMORY:
{relevant_memory}
"""
    return [
        {"role": "system", "content": system_prompt},
        *get_recent_history(user_id),
        {"role": "user", "content": prompt},
    ]


def chat_bot(prompt, history=None):
    prompt = (prompt or "").strip()
    if not prompt:
        return "Please enter a message."

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY is missing. Add it to the .env file and restart the app."

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODEL,
            messages=build_messages(prompt),
            temperature=0.3,
        )
        reply = response.choices[0].message.content
    except Exception as error:
        return f"The AI service could not answer: {error}"

    # Save only completed exchanges, so failed API calls do not pollute memory.
    save_memory("user", prompt)
    save_memory("assistant", reply)
    return reply


setup_database()

demo = gr.ChatInterface(
    fn=chat_bot,
    title="Context-Aware Learning Chatbot",
    description=(
        "Uses a learner profile, seed knowledge, recent chat, and keyword-retrieved "
        "SQLite memory."
    ),
)


if __name__ == "__main__":
    demo.launch()
