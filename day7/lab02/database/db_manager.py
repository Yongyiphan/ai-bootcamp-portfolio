"""SQLite persistence for review analysis records."""

import sqlite3
from datetime import datetime

import config


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(config.DB_NAME)


def init_db() -> None:
    """Create the summaries table when it does not exist."""
    with _connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                summary TEXT NOT NULL,
                rating INTEGER NOT NULL,
                category TEXT NOT NULL,
                created_at DATETIME NOT NULL
            )"""
        )


def save_summary(filename: str, summary: str, rating: int, category: str) -> int:
    """Save one analysis and return its database ID."""
    with _connect() as conn:
        cursor = conn.execute(
            """INSERT INTO summaries
               (filename, summary, rating, category, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (filename, summary, rating, category, datetime.now()),
        )
        return int(cursor.lastrowid)


def clear_summaries() -> None:
    """Delete all saved review summaries."""
    with _connect() as conn:
        conn.execute("DELETE FROM summaries")


def get_summaries_by_category(category: str) -> list[tuple]:
    """Return history rows in one sentiment category, newest first."""
    with _connect() as conn:
        return conn.execute(
            """SELECT id, filename, created_at
               FROM summaries WHERE category = ? ORDER BY created_at DESC""",
            (category,),
        ).fetchall()


def get_summary_by_id(summary_id: int) -> tuple | None:
    """Return one complete analysis record."""
    with _connect() as conn:
        return conn.execute(
            """SELECT filename, summary, rating, category, created_at
               FROM summaries WHERE id = ?""",
            (summary_id,),
        ).fetchone()
