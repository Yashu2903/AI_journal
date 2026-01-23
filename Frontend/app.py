import streamlit as st
import requests

api = "http://localhost:8000"

st.title("AI Memory Journal")

def check_api_connection():
    try:
        response = requests.get(f"{api}/docs", timeout=2)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False

if not check_api_connection():
    st.error("⚠️ Backend API is not running. Please start the FastAPI server first.")
    st.info("Run: `uvicorn backend.main:app --reload` from the project root")
    st.stop()

if "session_id" not in st.session_state:
    try:
        response = requests.post(f"{api}/sessions")
        response.raise_for_status()
        st.session_state.session_id = response.json()["session_id"]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create session: {e}")
        st.stop()

session_id = st.session_state.session_id
st.caption(f"Session ID: {session_id}")

try:
    history_response = requests.get(f"{api}/sessions/{session_id}/history")
    history_response.raise_for_status()
    history_data = history_response.json()
    for m in history_data["messages"]:
        with st.chat_message(m["role"]):
            st.write(m["content"])
except requests.exceptions.RequestException as e:
    st.warning(f"Failed to load history: {e}")

msg = st.chat_input("Enter a message")

if msg:
    try:
        response = requests.post(f"{api}/chat", json={"session_id": session_id, "role": "user", "content": msg})
        response.raise_for_status()
        assistant_msg = response.json()["reply"]

        with st.chat_message("assistant"):
            st.write(assistant_msg)
        st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to send message: {e}")
