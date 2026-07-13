"""
TUGAS ANGGOTA 3: MANAJEMEN SESI (Session Management) - IMPLEMENTASI REAL SQLITE
================================================================================
Implementasi manajemen sesi yang aman menggunakan database SQLite "bank.db".
"""

import time
import sqlite3
import uuid

DB_FILE = "bank.db"
SESSION_TIMEOUT = 6  # 1 minutes

def _get_conn() -> sqlite3.Connection:
    """Buka koneksi SQLite dengan foreign-key check aktif."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_session(user_id: str, role: str) -> str:
    """
    Membuat sesi baru di database SQLite setelah user berhasil melewati login ganda.
    
    Parameter:
    - user_id (str): Username/ID dari user yang login.
    - role (str): Role milik user (misal: 'customer' atau 'admin').
    
    Mengembalikan:
    - str: Token sesi yang dihasilkan untuk dikirim ke client.
    """
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
    """
    Memverifikasi apakah token sesi terdaftar di database SQLite dan belum kedaluwarsa.
    
    Parameter:
    - session_token (str): Token sesi dari client (Bearer token).
    
    Mengembalikan:
    - dict | None: Dictionary berisi {"user_id": ..., "role": ...} jika valid,
                   atau None jika token tidak valid/kedaluwarsa.
    """
    now = time.time()
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        # Bersihkan sesi-sesi lain yang sudah kedaluwarsa secara berkala
        cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
        
        # Cari sesi dengan token yang diberikan
        cursor.execute(
            "SELECT username, role, expires_at FROM sessions WHERE session_token = ?",
            (session_token,)
        )
        row = cursor.fetchone()
        
        if row:
            username, role, expires_at = row
            # Jika terdaftar dan belum kedaluwarsa, perbarui waktu kedaluwarsanya (sliding window)
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
    """
    Menghapus sesi dari database SQLite ketika user logout.
    
    Parameter:
    - session_token (str): Token sesi yang ingin dihapus.
    
    Mengembalikan:
    - bool: True jika berhasil dihapus, False jika tidak.
    """
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()
