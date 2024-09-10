import os

import requests
import streamlit as st

st.title("File Upload")

# Initialize session state for file processing status
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])

if uploaded_file is not None:
    st.write("File uploaded successfully!")

    # Prepare the file and data for sending to the backend
    files = {"file": uploaded_file.getvalue()}
    data = {"original_filename": uploaded_file.name}

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
    st.success("File processed state has been reset.")
