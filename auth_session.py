import time
import sqlite3
import uuid

DB_FILE = "bank.db"
SESSION_TIMEOUT = 10  # 6 sec

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_session(user_id: str, role: str) -> str:
    session_token = str(uuid.uuid4())
    expires_at = time.time() + SESSION_TIMEOUT
    
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_token, username, role, expires_at) VALUES (?, ?, ?, ?)",
            (session_token, user_id, role, expires_at)
        )
        conn.commit()
        return session_token
    finally:
        conn.close()

def verify_session(session_token: str) -> dict | None:
    now = time.time()
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
        
        cursor.execute(
            "SELECT username, role, expires_at FROM sessions WHERE session_token = ?",
            (session_token,)
        )
        row = cursor.fetchone()
        
        if row:
            username, role, expires_at = row
            new_expires = now + SESSION_TIMEOUT
            cursor.execute(
                "UPDATE sessions SET expires_at = ? WHERE session_token = ?",
                (new_expires, session_token)
            )
            conn.commit()
            return {
                "user_id": username,
                "role": role
            }
        conn.commit()
        return None
    finally:
        conn.close()

def destroy_session(session_token: str) -> bool:
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()
