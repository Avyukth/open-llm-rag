import os
from typing import List

import requests
import streamlit as st

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
st.title("Chat")

if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

if not st.session_state.file_processed:
    st.warning("Please upload and process a file before using the chat.")
    st.stop()


class Answer:
    def __init__(self, answer: str, sources: List[str]):
        self.answer = answer
        self.sources = sources


API_ENDPOINT = f"{BACKEND_URL}/api/qa/answer"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            st.markdown("**Sources:**")
            for source in message["sources"]:
                st.markdown(f"- {source}")

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(API_ENDPOINT, json={"question": prompt})
            if response.status_code == 200:
                answer_data = response.json()
                answer = Answer(**answer_data)
                st.markdown(answer.answer)
                if answer.sources:
                    st.markdown("**Sources:**")
                    for source in answer.sources:
                        st.markdown(f"- {source}")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer.answer,
                        "sources": answer.sources,
                    }
                )
            else:
                st.error(f"Error: {response.status_code} - {response.text}")

if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()
