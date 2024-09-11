import requests
import streamlit as st

st.set_page_config(page_title="Q&A App", page_icon="🤖")

if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

st.title("Q&A Application")
st.write("Welcome to the Q&A Application. Use the sidebar to navigate between pages.")
