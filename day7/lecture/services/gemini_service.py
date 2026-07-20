from google import genai
from google.genai import types
import day7.lecture.config as config

_client = None
_client_api_key = None


def _get_client():
    global _client, _client_api_key

    api_key = config.get_setting("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to day7/.env locally or "
            "to the Streamlit Community Cloud app secrets."
        )

    if _client is None or _client_api_key != api_key:
        if _client is not None:
            _client.close()
        _client = genai.Client(api_key=api_key)
        _client_api_key = api_key
    return _client


def _convert_to_gemini_contents(messages):
    formatted_contents = []
    for msg in messages:
        if msg['role'] == 'system':
            continue
        gemini_role = "model" if msg['role'] == "assistant" else "user"
        formatted_contents.append(
            types.Content(role=gemini_role, parts=[types.Part.from_text(text=msg['content'])])
        )
    return formatted_contents

def get_ai_response_stream(messages):
    client = _get_client()
    gemini_payload = _convert_to_gemini_contents(messages)
    system_prompt = config.get_setting(
        "SYSTEM_PROMPT", "You are a helpful AI assistant."
    )
    model = config.get_setting("GEMINI_MODEL", "gemini-3.5-flash")
    api_config = types.GenerateContentConfig(system_instruction=system_prompt)
    return client.models.generate_content_stream(
        model=model,
        contents=gemini_payload,
        config=api_config
    )

def parse_stream_chunks(raw_stream):
    for chunk in raw_stream:
        if chunk.text:
            yield chunk.text
