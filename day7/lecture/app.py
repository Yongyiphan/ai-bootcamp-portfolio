import streamlit as st

import day7.lecture.config as config
from database.db_manager import (
    create_session,
    get_chat_history,
    get_sessions,
    init_db,
    save_message,
)
from day7.lecture.services.gemini_service import get_ai_response_stream as get_gemini_stream
from day7.lecture.services.gemini_service import parse_stream_chunks as parse_gemini_chunks
from day7.lecture.services.llm_service import get_ollama_stream
from day7.lecture.services.llm_service import parse_stream_chunks as parse_ollama_chunks

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
    provider_setting = config.get_setting("DEFAULT_PROVIDER", "ollama").lower()
    default_provider = (
        provider_setting if provider_setting in providers else "ollama"
    )
    provider = st.selectbox(
        "AI Provider",
        providers,
        index=providers.index(default_provider),
        format_func=str.title,
    )

    if provider == "ollama":
        default_model = config.get_setting("DEFAULT_MODEL", "llama3.2:3b")
        model_name = st.text_input("Ollama Model", value=default_model)
        st.caption("Ollama requires access to your local Ollama server.")
    else:
        live_gemini_model = config.get_setting("GEMINI_MODEL", "gemini-3.5-flash")
        st.caption(f"Gemini model: {live_gemini_model}")

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
