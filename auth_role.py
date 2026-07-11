"""
TUGAS ANGGOTA 4: ROLE USER & TRANSAKSI (SETOR & TARIK) - IMPLEMENTASI FINAL
=================================================================================
Implementasi Role-Based Access Control (RBAC) dan transaksi keuangan
(setor/tarik tunai) yang terhubung langsung ke database SQLite "bank.db".

Catatan keamanan:
- check_role mencegah admin melakukan transaksi (hanya customer).
- Semua nominal divalidasi: harus > 0 (anti manipulasi nilai negatif/nol).
- Tarik tunai mempertahankan saldo minimum Rp 50.000,00.
- Transaksi dicatat permanen di tabel `transactions` (audit trail).
"""

import sqlite3

DB_FILE = "bank.db"

# Saldo minimum yang harus tersisa di rekening setelah penarikan
MINIMUM_BALANCE = 50000.0


def _get_conn() -> sqlite3.Connection:
    """Buka koneksi SQLite dengan foreign-key check aktif."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def check_role(user_role: str, required_role: str) -> bool:
    """
    Memeriksa apakah role user memenuhi role yang dibutuhkan untuk mengakses fitur tertentu.

    Parameter:
    - user_role (str): Role milik pengguna saat ini (diperoleh dari data sesi).
    - required_role (str): Role minimal yang diperlukan untuk mengakses fitur.

    Mengembalikan:
    - bool: True jika role memenuhi syarat, False jika ditolak.
    """
    return user_role == required_role


def process_deposit(user_id: str, amount: float) -> dict:
    """
    Memproses penambahan saldo (setor tunai) langsung pada database SQLite.

    Parameter:
    - user_id (str): Username/ID user yang ingin menyetor uang.
    - amount (float): Jumlah uang yang akan disetor.

    Mengembalikan:
    - dict: {"success": bool, "message": str, "new_balance": float}
    """
    # Validasi: nominal harus positif
    if amount <= 0:
        return {
            "success": False,
            "message": "Nominal setor tunai harus lebih besar dari Rp 0,00.",
            "new_balance": get_balance(user_id),
        }

    conn = _get_conn()
    try:
        cursor = conn.cursor()
        # Ambil saldo saat ini
        cursor.execute("SELECT balance FROM balances WHERE username = ?", (user_id,))
        row = cursor.fetchone()
        if row is None:
            # Auto-create baris saldo jika belum ada (safety net)
            cursor.execute(
                "INSERT INTO balances (username, balance) VALUES (?, ?)",
                (user_id, 0.0),
            )
            current = 0.0
        else:
            current = row[0]

        new_balance = current + amount
        cursor.execute(
            "UPDATE balances SET balance = ? WHERE username = ?",
            (new_balance, user_id),
        )
        # Audit trail
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS transactions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "username TEXT NOT NULL, "
            "type TEXT NOT NULL, "
            "amount REAL NOT NULL, "
            "balance_after REAL NOT NULL, "
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        cursor.execute(
            "INSERT INTO transactions (username, type, amount, balance_after) "
            "VALUES (?, 'deposit', ?, ?)",
            (user_id, amount, new_balance),
        )
        conn.commit()
        return {
            "success": True,
            "message": f"Setor tunai berhasil sebesar Rp {amount:,.2f}",
            "new_balance": new_balance,
        }
    except sqlite3.Error as e:
        conn.rollback()
        return {
            "success": False,
            "message": f"Terjadi kesalahan database: {str(e)}",
            "new_balance": get_balance(user_id),
        }
    finally:
        conn.close()


def process_withdraw(user_id: str, amount: float) -> dict:
    """
    Memproses pengurangan saldo (tarik tunai) langsung pada database SQLite.

    Parameter:
    - user_id (str): Username/ID user yang ingin menarik uang.
    - amount (float): Jumlah uang yang akan ditarik.

    Mengembalikan:
    - dict: {"success": bool, "message": str, "new_balance": float}
    """
    current = get_balance(user_id)

    # Validasi: user terdaftar
    if current is None:
        return {
            "success": False,
            "message": "Rekening tidak ditemukan.",
            "new_balance": 0.0,
        }

    # Validasi: nominal harus positif
    if amount <= 0:
        return {
            "success": False,
            "message": "Nominal tarik tunai harus lebih besar dari Rp 0,00.",
            "new_balance": current,
        }

    # Validasi: saldo sisa tidak boleh di bawah saldo minimum
    if current - amount < MINIMUM_BALANCE:
        return {
            "success": False,
            "message": (
                f"Tarik tunai gagal. Saldo setelah penarikan "
                f"(Rp {current - amount:,.2f}) akan turun di bawah saldo minimum "
                f"Rp {MINIMUM_BALANCE:,.2f}."
            ),
            "new_balance": current,
        }

    conn = _get_conn()
    try:
        cursor = conn.cursor()
        new_balance = current - amount
        cursor.execute(
            "UPDATE balances SET balance = ? WHERE username = ?",
            (new_balance, user_id),
        )
        # Audit trail
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS transactions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "username TEXT NOT NULL, "
            "type TEXT NOT NULL, "
            "amount REAL NOT NULL, "
            "balance_after REAL NOT NULL, "
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        cursor.execute(
            "INSERT INTO transactions (username, type, amount, balance_after) "
            "VALUES (?, 'withdraw', ?, ?)",
            (user_id, amount, new_balance),
        )
        conn.commit()
        return {
            "success": True,
            "message": f"Tarik tunai berhasil sebesar Rp {amount:,.2f}",
            "new_balance": new_balance,
        }
    except sqlite3.Error as e:
        conn.rollback()
        return {
            "success": False,
            "message": f"Terjadi kesalahan database: {str(e)}",
            "new_balance": current,
        }
    finally:
        conn.close()


def get_balance(user_id: str) -> float:
    """
    Mendapatkan saldo saat ini untuk user tertentu dari database SQLite.
    Mengembalikan 0.0 jika user belum punya baris saldo.
    """
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM balances WHERE username = ?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 0.0
    finally:
        conn.close()
