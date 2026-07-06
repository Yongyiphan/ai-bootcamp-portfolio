import streamlit as st
from chatbot import chat

st.set_page_config(page_title="Memory Chatbot", layout="centered")
st.title("💬 Memory Chatbot")
st.caption("A stateful chatbot with long-term memory using Mem0")

if "history" not in st.session_state:
    st.session_state.history = []

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        response = chat(user_input, st.session_state.history[:-1])
        st.markdown(response)
    
    st.session_state.history.append({"role": "assistant", "content": response})
