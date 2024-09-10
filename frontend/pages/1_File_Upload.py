import os

import requests
import streamlit as st

st.title("File Upload and Model Selection")

# Initialize session state for file processing status and model selections
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False
if "model_provider" not in st.session_state:
    st.session_state.model_provider = "Ollama"
if "model_name" not in st.session_state:
    st.session_state.model_name = "llama3.1:8b"

# Define available model providers and their corresponding models
MODEL_PROVIDERS = {
    "Ollama": ["llama3.1:8b", "llama2", "mistral", "vicuna"],
    "OpenAI": ["gpt-3.5-turbo", "gpt-4"],
    "Cohere": ["command", "command-light"],
}

# Mapping between display names and backend identifiers
PROVIDER_MAPPING = {"Ollama": "ollama", "OpenAI": "openai", "Cohere": "cohere"}

# Model provider selection
model_provider = st.selectbox(
    "Select Model Provider",
    options=list(MODEL_PROVIDERS.keys()),
    index=list(MODEL_PROVIDERS.keys()).index("Ollama"),
    key="model_provider",
)

# Model name selection based on the selected provider
model_name = st.selectbox(
    "Select Model",
    options=MODEL_PROVIDERS[model_provider],
    index=(
        MODEL_PROVIDERS[model_provider].index("llama3.1:8b")
        if "llama3.1:8b" in MODEL_PROVIDERS[model_provider]
        else 0
    ),
    key="model_name",
)

uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])

if uploaded_file is not None:
    st.write("File uploaded successfully!")

    # Prepare the file and data for sending to the backend
    files = {"file": uploaded_file.getvalue()}
    data = {
        "original_filename": uploaded_file.name,
        "model_provider": PROVIDER_MAPPING[
            model_provider
        ],  # Use the backend identifier
        "model_name": model_name,
    }

    # Send file to backend for processing
    try:
        response = requests.post(
            "http://localhost:8000/api/files/upload", files=files, data=data
        )

        if response.status_code == 200:
            result = response.json()
            st.success(
                f"File processed successfully! Saved as: {result['saved_filename']}"
            )
            st.session_state.file_processed = True

            # Display additional information
            st.write(f"Original filename: {result['original_filename']}")
            st.write(f"Detected extension: {result['detected_extension']}")
            st.write(f"Selected Model Provider: {model_provider}")  # Display name
            st.write(f"Selected Model: {model_name}")
        else:
            st.error(f"Error processing file: {response.text}")
    except requests.RequestException as e:
        st.error(f"Error connecting to the server: {str(e)}")

if st.session_state.file_processed:
    st.write(
        "You can now switch to the Chat page to ask questions about the uploaded document."
    )

# Add a button to reset the file processed state (useful for testing)
if st.button("Reset File Processed State"):
    st.session_state.file_processed = False
    st.session_state.model_provider = "Ollama"
    st.session_state.model_name = "llama3.1:8b"
    st.success("File processed state and model selections have been reset.")
