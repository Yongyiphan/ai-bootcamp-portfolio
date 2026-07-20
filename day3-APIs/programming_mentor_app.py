import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

SYSTEM_PROMPT = """You are a patient programming mentor for beginner and intermediate learners.
Follow these rules in every response:
1. Explain the reasoning behind a solution before showing any code.
2. If a problem is incomplete or ambiguous, ask a focused clarifying question before solving it.
3. Use Python for examples unless the learner requests another language.
4. When debugging, identify and explain the root cause before suggesting a fix.
5. Encourage best practices and explain common mistakes in a respectful, supportive tone.
6. Guide the learner with small steps and useful hints instead of giving an unexplained final answer.
7. Remember details shared earlier in the conversation and adapt explanations to the learner's background.
"""

st.set_page_config(page_title="Programming Mentor", page_icon="💻")
st.title("💻 Programming Mentor")
st.caption("Ask about programming concepts, code, errors, or practice exercises.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

with st.sidebar:
    st.header("Session")
    st.metric("Tokens used", st.session_state.total_tokens)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("What would you like help with?")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY was not found. Add it to the project .env file and restart Streamlit.")
        st.stop()

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}]
                    + st.session_state.messages,
                    temperature=0.2,
                    max_tokens=400,
                )
                answer = response.choices[0].message.content or "I could not generate a response."
                st.session_state.total_tokens += response.usage.total_tokens
                st.markdown(answer)
            except Exception as error:
                st.error(f"The request failed: {error}")
                st.stop()

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
