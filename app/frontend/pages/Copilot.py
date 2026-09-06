import streamlit as st
import requests
from auth import require_auth

require_auth()
API_URL = "https://retailmind-ai-7h7v.onrender.com"

st.title("💬 Retailer Copilot")
st.write("Ask any question about your business in plain English.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for entry in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(entry["question"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])

question = st.chat_input("Ask a question about your business...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_URL}/copilot",
                json={
                    "question": question,
                    "history": st.session_state.chat_history
                }
            )

        if response.status_code == 200:
            answer = response.json()
            st.write(str(answer))
            st.session_state.chat_history.append({"question": question, "answer": answer})
        else:
            st.error("Something went wrong. Try again.")

if st.button("Clear conversation"):
    st.session_state.chat_history = []
    st.rerun()