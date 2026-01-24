import streamlit as st
import requests
from datetime import datetime

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
# Session Management Functions
# -------------------------------
def get_all_sessions():
    """Fetch all sessions from backend."""
    try:
        response = requests.get(f"{api}/sessions")
        response.raise_for_status()
        return response.json()["sessions"]
    except requests.exceptions.RequestException:
        return []

def create_new_session(session_name: str = None):
    """Create a new session."""
    try:
        payload = {}
        if session_name:
            payload["session_name"] = session_name
        response = requests.post(f"{api}/sessions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["session_id"], data["session_name"]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create session: {e}")
        return None, None

def rename_session(session_id: str, new_name: str):
    """Rename a session."""
    try:
        response = requests.patch(
            f"{api}/sessions/{session_id}",
            json={"session_name": new_name}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False

def get_session_name(session_id: str):
    """Get the name of a session."""
    sessions = get_all_sessions()
    for session in sessions:
        if session["session_id"] == session_id:
            return session["session_name"]
    return "Unknown Session"

# -------------------------------
# Sidebar: Session Selector
# -------------------------------
with st.sidebar:
    st.header("📂 Sessions")
    
    # Fetch all sessions
    all_sessions = get_all_sessions()
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
        st.session_state.session_name = None
    
    # Session selector dropdown
    if all_sessions:
        session_options = {
            f"{s['session_name']} ({s['message_count']} msgs)": s["session_id"]
            for s in all_sessions
        }
        
        # Find current session name for display
        current_display = None
        if st.session_state.session_id:
            for name, sid in session_options.items():
                if sid == st.session_state.session_id:
                    current_display = name
                    break
        
        selected_display = st.selectbox(
            "Select Session",
            options=list(session_options.keys()),
            index=list(session_options.keys()).index(current_display) if current_display else 0,
            key="session_selector"
        )
        
        if selected_display:
            selected_id = session_options[selected_display]
            if selected_id != st.session_state.session_id:
                st.session_state.session_id = selected_id
                st.session_state.session_name = selected_display.split(" (")[0]
                st.rerun()
    else:
        st.info("No sessions yet. Create one below!")
    
    st.divider()
    
    # New Session button
    if st.button("➕ New Session", use_container_width=True):
        session_id, session_name = create_new_session()
        if session_id:
            st.session_state.session_id = session_id
            st.session_state.session_name = session_name
            st.success(f"Created: {session_name}")
            st.rerun()
    
    # Rename Session button
    if st.session_state.session_id:
        st.divider()
        with st.expander("✏️ Rename Session"):
            new_name = st.text_input(
                "New name",
                value=st.session_state.session_name or "",
                key="rename_input"
            )
            if st.button("Save", use_container_width=True):
                if new_name and new_name.strip():
                    if rename_session(st.session_state.session_id, new_name.strip()):
                        st.session_state.session_name = new_name.strip()
                        st.success("Session renamed!")
                        st.rerun()
                    else:
                        st.error("Failed to rename session")

# -------------------------------
# Main Chat Interface
# -------------------------------
if not st.session_state.session_id:
    st.info("👈 Please select or create a session from the sidebar to start chatting.")
    st.stop()

session_id = st.session_state.session_id
session_name = st.session_state.session_name or get_session_name(session_id)

# Display session name instead of UUID
st.caption(f"💬 {session_name}")

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
# Handle message sending
# -------------------------------
if msg:
    try:
        # Call chat endpoint
        response = requests.post(
            f"{api}/chat",
            json={"session_id": session_id, "role": "user", "content": msg}
        )
        response.raise_for_status()
        
        # Refresh session name in case it was auto-renamed
        updated_name = get_session_name(session_id)
        if updated_name != session_name:
            st.session_state.session_name = updated_name

        # 🔽 Recall memories from backend
        recall_response = requests.get(
            f"{api}/debug/recall",
            params={"q": msg, "session_id": session_id}
        )
        recall_response.raise_for_status()
        recall_data = recall_response.json()

        # 🔽 Show recalled memories
        if recall_data["memories"]:
            with st.expander("🧠 Recalled Memories"):
                for m in recall_data["memories"]:
                    st.write("•", m)

        st.rerun()

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to send message: {e}")
