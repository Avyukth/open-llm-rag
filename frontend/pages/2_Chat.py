import os
import time
from typing import List

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.set_page_config(layout="wide")
st.title("Chat")

# Check if file has been processed
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

if not st.session_state.file_processed:
    st.warning(
        "Please upload and process a file in the File Upload page before using the chat."
    )
    st.stop()


class Answer:
    def __init__(self, answer: str, sources: List[str]):
        self.answer = answer
        self.sources = sources


API_ENDPOINT = f"{BACKEND_URL}/api/qa/answer"
METRICS_ENDPOINT = f"{BACKEND_URL}/api/qa/metrics"

if "messages" not in st.session_state:
    st.session_state.messages = []


def fetch_metrics():
    with st.spinner("Fetching metrics..."):
        metrics_response = requests.get(METRICS_ENDPOINT)
        if metrics_response.status_code == 200:
            return metrics_response.json()
    return None


# Metrics sidebar
with st.sidebar:
    st.title("Performance Metrics")
    if st.button("Fetch Metrics"):
        metrics = fetch_metrics()
        if metrics:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Hit Rate", f"{metrics['hit_rate']:.2%}")
            with col2:
                st.metric("MRR", f"{metrics['mrr']:.2f}")
            st.info(
                """
            **Hit Rate**: Percentage of relevant answers
            **MRR**: Mean Reciprocal Rank (1.0 is best)
            """
            )
            st.text(f"Last updated: {time.strftime('%H:%M:%S')}")
        else:
            st.error("Failed to fetch metrics. Please try again.")

# Main chat area
chat_container = st.container()

# Chat messages display
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                st.markdown("**Sources:**")
                for source in message["sources"]:
                    st.markdown(f"- {source}")

# Chat input at the bottom
prompt = st.chat_input("Ask a question")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
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

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()
