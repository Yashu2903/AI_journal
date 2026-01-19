import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..schemas import Role

DB_PATH = Path(__file__).parent.parent / "journal.db"

_conn: Optional[sqlite3.Connection] = None

def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn

def init_db() -> None:
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    conn.commit()

def create_session(session_id: str) -> None:
    conn = get_conn()

    conn.execute("""
        INSERT OR IGNORE INTO sessions (session_id, created_at) VALUES (?, CURRENT_TIMESTAMP)
    """, (session_id,))
    conn.commit()

def add_message(session_id: str, role: Role, content: str) -> int:
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (session_id, role, content))
    conn.commit()
    return int(cursor.lastrowid)

def get_history(session_id: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, session_id, role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at ASC
    """, (session_id,))

    rows = cursor.fetchall()

    out: List[Dict[str, Any]] = []

    for row in rows:
        out.append({
            "id": row["id"],
            "session_id": row["session_id"],
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"]
        })
    
    return out
