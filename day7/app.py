import os

import streamlit as st

import config
from database.db_manager import (
    create_session,
    get_chat_history,
    get_sessions,
    init_db,
    save_message,
)
from services.gemini_service import get_ai_response_stream as get_gemini_stream
from services.gemini_service import parse_stream_chunks as parse_gemini_chunks
from services.llm_service import get_ollama_stream
from services.llm_service import parse_stream_chunks as parse_ollama_chunks

st.set_page_config(page_title="AI SQLite Chatbot", layout="wide")
init_db()

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

with st.sidebar:
    st.title("Chat History")

    if st.button("New Chat", use_container_width=True):
        st.session_state.current_session_id = create_session()
        st.rerun()

    st.divider()
    sessions = get_sessions()
    for s_id, s_title in sessions:
        if st.button(s_title, key=f"session_{s_id}", use_container_width=True):
            st.session_state.current_session_id = s_id
            st.rerun()

    st.divider()
    providers = ["ollama", "gemini"]
    default_provider = (
        config.DEFAULT_PROVIDER if config.DEFAULT_PROVIDER in providers else "ollama"
    )
    provider = st.selectbox(
        "AI Provider",
        providers,
        index=providers.index(default_provider),
        format_func=str.title,
    )

    if provider == "ollama":
        model_name = st.text_input("Ollama Model", value=config.DEFAULT_MODEL)
        st.caption("Ollama requires access to your local Ollama server.")
    else:
        model_source = config.SETTING_SOURCES.get("GEMINI_MODEL", "unknown")
        st.caption(f"Gemini model: {config.GEMINI_MODEL}")
        st.caption(f"Model setting source: {model_source}")

    with st.expander("Configuration debug"):
        secret_model = st.secrets.get("GEMINI_MODEL", "<missing>")
        environment_model = os.getenv("GEMINI_MODEL", "<missing>")
        st.code(
            "\n".join(
                [
                    f"st.secrets GEMINI_MODEL: {secret_model}",
                    f"os.getenv GEMINI_MODEL: {environment_model}",
                    f"config.GEMINI_MODEL: {config.GEMINI_MODEL}",
                    f"config source: {config.SETTING_SOURCES.get('GEMINI_MODEL', 'unknown')}",
                ]
            )
        )

st.title("AI Chat")

if st.session_state.current_session_id is None:
    st.info("Start a new chat or select history from the sidebar.")
else:
    chat_history = get_chat_history(st.session_state.current_session_id)
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        save_message(st.session_state.current_session_id, "user", prompt)

        with st.chat_message("assistant"):
            try:
                if provider == "gemini":
                    messages = chat_history + [{"role": "user", "content": prompt}]
                    raw_stream = get_gemini_stream(messages)
                    clean_text_stream = parse_gemini_chunks(raw_stream)
                else:
                    raw_stream = get_ollama_stream(model_name, chat_history, prompt)
                    clean_text_stream = parse_ollama_chunks(raw_stream)

                full_response = st.write_stream(clean_text_stream)
                save_message(
                    st.session_state.current_session_id, "assistant", full_response
                )
            except Exception as error:
                st.error(f"{provider.title()} error: {error}")
