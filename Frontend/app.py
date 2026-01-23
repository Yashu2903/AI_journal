import streamlit as st
import requests

api = "http://localhost:8000"

st.title("AI Memory Journal")

# -------------------------------
# API health check
# -------------------------------
def check_api_connection():
    try:
        requests.get(f"{api}/docs", timeout=2)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False

if not check_api_connection():
    st.error("⚠️ Backend API is not running. Please start the FastAPI server first.")
    st.info("Run: `uvicorn backend.main:app --reload` from the project root")
    st.stop()

# -------------------------------
# Session handling
# -------------------------------
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

# -------------------------------
# Load & render history
# -------------------------------
try:
    history_response = requests.get(f"{api}/sessions/{session_id}/history")
    history_response.raise_for_status()
    history_data = history_response.json()
    for m in history_data["messages"]:
        with st.chat_message(m["role"]):
            st.write(m["content"])
except requests.exceptions.RequestException as e:
    st.warning(f"Failed to load history: {e}")

# -------------------------------
# Chat input
# -------------------------------
msg = st.chat_input("Enter a message")

# -------------------------------
# Feature 4: memory recall panel
# -------------------------------
if msg:
    try:
        # call chat endpoint
        response = requests.post(
            f"{api}/chat",
            json={"session_id": session_id, "role": "user", "content": msg}
        )
        response.raise_for_status()

        # 🔽 NEW: recall memories from backend
        recall_response = requests.get(
            f"{api}/debug/recall",
            params={"q": msg, "session_id": session_id}
        )
        recall_response.raise_for_status()
        recall_data = recall_response.json()

        # 🔽 NEW: show recalled memories
        if recall_data["memories"]:
            with st.expander("🧠 Recalled Memories"):
                for m in recall_data["memories"]:
                    st.write("•", m)

        st.rerun()

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to send message: {e}")
