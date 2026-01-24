import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..schemas import Role

# Database file in data/ directory at project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "journal.db"

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
            session_name TEXT DEFAULT 'New Conversation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add session_name column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN session_name TEXT DEFAULT 'New Conversation'")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists, ignore
        pass

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

def create_session(session_id: str, session_name: Optional[str] = None) -> None:
    """Create a new session with optional name."""
    conn = get_conn()
    
    if session_name is None:
        # Generate default name based on timestamp
        from datetime import datetime
        now = datetime.now()
        session_name = f"Chat - {now.strftime('%b %d, %I:%M %p')}"
    
    conn.execute("""
        INSERT OR IGNORE INTO sessions (session_id, session_name, created_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (session_id, session_name))
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

def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all sessions with metadata including message counts."""
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            s.session_id,
            s.session_name,
            s.created_at,
            COUNT(m.id) as message_count
        FROM sessions s
        LEFT JOIN messages m ON s.session_id = m.session_id
        GROUP BY s.session_id, s.session_name, s.created_at
        ORDER BY s.created_at DESC
    """)
    
    rows = cursor.fetchall()
    
    out: List[Dict[str, Any]] = []
    for row in rows:
        out.append({
            "session_id": row["session_id"],
            "session_name": row["session_name"],
            "created_at": row["created_at"],
            "message_count": row["message_count"]
        })
    
    return out

def update_session_name(session_id: str, new_name: str) -> bool:
    """Update the name of a session."""
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE sessions 
        SET session_name = ? 
        WHERE session_id = ?
    """, (new_name, session_id))
    
    conn.commit()
    return cursor.rowcount > 0

def get_session_name(session_id: str) -> Optional[str]:
    """Get the name of a session."""
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT session_name FROM sessions WHERE session_id = ?
    """, (session_id,))
    
    row = cursor.fetchone()
    return row["session_name"] if row else None
