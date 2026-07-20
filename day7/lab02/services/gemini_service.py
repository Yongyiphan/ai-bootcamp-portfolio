"""Gemini sentiment analysis service with no Streamlit dependencies."""

from google import genai
from google.genai import types

import config


SYSTEM_PROMPT = (
    "You are a database-integrated text processing utility. Analyze the user "
    "text data. You MUST output your response in a strict formatted style "
    "containing two sections:\n"
    "1. A bulleted summary synthesized from the reviews.\n"
    "2. A standalone single line stating exactly: 'FINAL_RATING: X' "
    "(where X is an integer score from 0 to 10).\n\n"
    "Keep your response analytical and professional."
)


def _parse_analysis_output(raw_output: str) -> tuple[str, int, str]:
    """Extract the clean summary, bounded rating, and category."""
    rating = 5
    clean_summary = raw_output.strip()

    if "FINAL_RATING:" in raw_output:
        summary_part, rating_part = raw_output.split("FINAL_RATING:", 1)
        clean_summary = summary_part.strip()
        try:
            digits = "".join(filter(str.isdigit, rating_part))
            rating = int(digits)
        except ValueError:
            rating = 5

    # Treat malformed out-of-range model output as the safe fallback rating.
    if not 0 <= rating <= 10:
        rating = 5

    if rating >= 8:
        category = "Good"
    elif rating >= 4:
        category = "Average"
    else:
        category = "Bad"
    return clean_summary, rating, category


def analyze_review_sentiment(review_content: str) -> tuple[str, int, str]:
    """Analyze review text and return ``(summary, rating, category)``."""
    if not review_content.strip():
        raise ValueError("The review file is empty.")

    client = genai.Client(api_key=config.require_gemini_api_key())
    try:
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=review_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return _parse_analysis_output(response.text)
    finally:
        client.close()
