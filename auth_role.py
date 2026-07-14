import sqlite3

DB_FILE = "bank.db"

MINIMUM_BALANCE = 50000.0


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def check_role(user_role: str, required_role: str) -> bool:
    return user_role == required_role


def process_deposit(user_id: str, amount: float) -> dict:
    if amount <= 0:
        return {
            "success": False,
            "message": "Nominal setor tunai harus lebih besar dari Rp 0,00.",
            "new_balance": get_balance(user_id),
        }

    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM balances WHERE username = ?", (user_id,))
        row = cursor.fetchone()
        if row is None:
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
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM balances WHERE username = ?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 0.0
    finally:
        conn.close()
