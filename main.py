from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import 4 berkas fitur modular (tugas masing-masing anggota)
import auth_hash
import auth_otp
import auth_session
import auth_role

app = FastAPI(title="Secure Digital Banking with MFA - SQLite Version")

# Setup Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# ================= DATABASE INITIALIZATION =================
@app.on_event("startup")
def startup_event():
    """
    Inisialisasi database SQLite 'bank.db' dan tabel yang diperlukan
    saat server pertama kali berjalan.
    """
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    
    # 1. Tabel users (Untuk Anggota 1 & Anggota 2)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    # Migrasi aman: tambahkan kolom email jika tabel users sudah ada sebelumnya tanpa kolom email
    try:
        cursor.execute("SELECT email FROM users LIMIT 1")
    except sqlite3.OperationalError:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            conn.commit()
            print("[SERVER] Kolom 'email' berhasil ditambahkan ke tabel 'users'.")
        except sqlite3.Error as e:
            print(f"[SERVER ERROR] Gagal menambahkan kolom email: {e}")
    
    # 2. Tabel balances (Untuk Anggota 4)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balances (
            username TEXT PRIMARY KEY,
            balance REAL NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    
    # 3. Tabel otps (Untuk Anggota 2)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otps (
            username TEXT PRIMARY KEY,
            otp_code TEXT NOT NULL,
            expires_at REAL NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    
    # 4. Tabel sessions (Untuk Anggota 3)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            expires_at REAL NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    
    # Seeding data bawaan jika database masih kosong
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Seeding satu-satunya akun admin bawaan dengan email default
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)", 
                       ("admin", "admin@gmail.com", auth_hash.hash_password("admin123"), "admin")) # Password asli: admin123
        
        # Seeding saldo awal untuk testing
        cursor.execute("INSERT INTO balances (username, balance) VALUES (?, ?)", ("admin", 0.0))
        
    conn.commit()
    conn.close()
    print("\n[SERVER] Database SQLite 'bank.db' berhasil diinisialisasi dan di-seed dengan sukses.\n")

# ================= PYDANTIC SCHEMAS =================
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class VerifyOTPRequest(BaseModel):
    username: str
    otp_code: str

class TransactionRequest(BaseModel):
    amount: float

# ================= AUTHENTICATION DEPENDENCY =================
def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Dependency untuk memvalidasi token sesi dari request header.
    Mengambil data session dari SQLite melalui auth_session.py.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token sesi tidak disediakan atau format salah.")
    
    token = authorization.split(" ")[1]
    
    # Memanggil verifikasi sesi dari auth_session.py (Anggota 3)
    session_data = auth_session.verify_session(token)
    if not session_data:
        raise HTTPException(status_code=401, detail="Sesi tidak valid atau telah kedaluwarsa.")
        
    return session_data

# ================= ROUTES =================

@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    """Menampilkan halaman utama Frontend Bank Digital."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/register")
def register(req: RegisterRequest):
    """
    Registrasi user baru dengan role customer secara otomatis dengan email.
    """
    username = req.username.strip().lower()
    email = req.email.strip().lower()
    password = req.password
    
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username minimal terdiri dari 3 karakter.")
    if len(email) < 5 or "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Alamat email tidak valid. Masukkan email Gmail yang benar.")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password minimal terdiri dari 6 karakter.")
        
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username sudah terdaftar. Silakan pilih username lain.")
            
        # Check if email already exists
        cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Alamat email sudah digunakan. Silakan gunakan email lain.")
        
        # Hash the password
        hashed = auth_hash.hash_password(password)
        
        # Insert user into users with email
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       (username, email, hashed, "customer"))
        
        # Seed initial balance (Rp 100.000,00)
        cursor.execute("INSERT INTO balances (username, balance) VALUES (?, ?)", (username, 100000.0))
        
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal melakukan registrasi: {str(e)}")
    finally:
        conn.close()
        
    return {
        "success": True,
        "message": f"Registrasi berhasil! Akun {username} siap digunakan."
    }
 
@app.post("/api/login")
def login(req: LoginRequest):
    """
    Step 1: Login Username & Password.
    Mengambil password hash dari SQLite dan memvalidasi menggunakan auth_hash.py.
    """
    username = req.username.strip().lower()
    password = req.password
    
    # Query database SQLite untuk mencari user beserta email-nya
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role, email FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=400, detail="Username atau password salah.")
        
    db_password_hash, role, email = row
    
    # 1. Validasi password menggunakan modul auth_hash.py (Anggota 1)
    is_valid = auth_hash.verify_password(password, db_password_hash)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Username atau password salah.")
        
    # 2. Jika user adalah admin, lewati OTP dan langsung buat session
    if role == "admin":
        session_token = auth_session.create_session(username, role)
        print(f"\n[SERVER] Admin {username} login berhasil tanpa OTP.\n")
        return {
            "success": True,
            "requires_otp": False,
            "token": session_token,
            "message": "Login berhasil sebagai Administrator."
        }
        
    # 3. Jika user adalah customer, buat OTP menggunakan modul auth_otp.py (Anggota 2)
    otp_code = auth_otp.generate_otp(username)
    
    # Mencetak kode OTP di console server untuk simulasi pengujian
    print(f"\n[SERVER BANNER] OTP untuk {username} adalah: {otp_code}\n")
    
    # Masking email untuk privasi pada UI
    masked_email = "email terdaftar"
    if email:
        parts = email.split("@")
        if len(parts) == 2:
            name_part, domain_part = parts
            if len(name_part) > 2:
                masked_name = name_part[0] + "*" * (len(name_part) - 2) + name_part[-1]
            else:
                masked_name = name_part[0] + "*" * len(name_part)
            masked_email = f"{masked_name}@{domain_part}"
    
    return {
        "success": True, 
        "requires_otp": True,
        "message": f"Password terverifikasi. OTP telah dikirim ke {masked_email}.", 
        "username": username
    }

@app.post("/api/verify-otp")
def verify_otp_endpoint(req: VerifyOTPRequest):
    """
    Step 2: Verifikasi OTP ganda.
    Memeriksa OTP di SQLite dan membuat sesi login di tabel sessions.
    """
    username = req.username.strip().lower()
    otp_code = req.otp_code.strip()
    
    # Ambil data user dari database SQLite
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=400, detail="User tidak terdaftar.")
        
    user_role = row[0]
        
    # 1. Verifikasi kode OTP dengan modul auth_otp.py (Anggota 2)
    is_otp_valid = auth_otp.verify_otp(username, otp_code)
    if not is_otp_valid:
        raise HTTPException(status_code=400, detail="Kode OTP salah atau telah kedaluwarsa.")
        
    # 2. Jika OTP valid, buat sesi login menggunakan modul auth_session.py (Anggota 3)
    session_token = auth_session.create_session(username, user_role)
    
    return {
        "success": True,
        "message": "Login berhasil.",
        "token": session_token
    }

@app.get("/api/dashboard")
def get_dashboard(current_user: dict = Depends(get_current_user)):
    """
    Mengambil data Dashboard Nasabah (Memerlukan login).
    Menampilkan detail User, Role (Anggota 4) dan Saldo (Anggota 4) dari SQLite.
    """
    username = current_user["user_id"]
    role = current_user["role"]
    
    # Mengambil saldo terkini dari database SQLite balances (Anggota 4)
    balance = auth_role.get_balance(username)
    
    return {
        "success": True,
        "username": username,
        "role": role,
        "balance": balance
    }

@app.post("/api/deposit")
def deposit(req: TransactionRequest, current_user: dict = Depends(get_current_user)):
    """
    Transaksi Setor Tunai (Hanya untuk Customer).
    Menggunakan auth_role.py (Tugas Anggota 4) untuk pengecekan role dan proses saldo.
    """
    username = current_user["user_id"]
    role = current_user["role"]
    
    # 1. Cek role terlebih dahulu menggunakan modul auth_role.py (Anggota 4)
    if not auth_role.check_role(role, "customer"):
        raise HTTPException(status_code=403, detail="Hak akses ditolak. Administrator tidak diijinkan bertransaksi keuangan.")
        
    # 2. Proses setoran ke SQLite
    result = auth_role.process_deposit(username, req.amount)
    return result

@app.post("/api/withdraw")
def withdraw(req: TransactionRequest, current_user: dict = Depends(get_current_user)):
    """
    Transaksi Tarik Tunai (Hanya untuk Customer).
    Menggunakan auth_role.py (Tugas Anggota 4) untuk pengecekan role dan proses saldo.
    """
    username = current_user["user_id"]
    role = current_user["role"]
    
    # 1. Cek role menggunakan modul auth_role.py (Anggota 4)
    if not auth_role.check_role(role, "customer"):
        raise HTTPException(status_code=403, detail="Hak akses ditolak. Administrator tidak diijinkan bertransaksi keuangan.")
        
    # 2. Proses penarikan saldo dari SQLite
    result = auth_role.process_withdraw(username, req.amount)
    
    # Jika transaksi gagal (misal saldo tidak mencukupi), kembalikan HTTP 400
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@app.post("/api/logout")
def logout(authorization: str = Header(None)):
    """
    Mengakhiri sesi login (Menghapus baris sesi di SQLite).
    Menggunakan auth_session.py (Tugas Anggota 3).
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        auth_session.destroy_session(token)
    return {"success": True, "message": "Logout sukses."}

@app.get("/api/admin/users")
def admin_get_users(current_user: dict = Depends(get_current_user)):
    """
    Mengambil daftar seluruh nasabah beserta saldo rekening mereka (Hanya untuk Admin).
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Hak akses ditolak. Hanya untuk administrator.")
        
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.username, u.role, COALESCE(b.balance, 0.0) 
            FROM users u
            LEFT JOIN balances b ON u.username = b.username
            WHERE u.role != 'admin'
        """)
        rows = cursor.fetchall()
        users_list = [{"username": r[0], "role": r[1], "balance": r[2]} for r in rows]
        return {"success": True, "users": users_list}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data nasabah: {str(e)}")
    finally:
        conn.close()

@app.get("/api/admin/transactions")
def admin_get_transactions(current_user: dict = Depends(get_current_user)):
    """
    Mengambil seluruh riwayat transaksi audit trail sistem (Hanya untuk Admin).
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Hak akses ditolak. Hanya untuk administrator.")
        
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    try:
        # Buat tabel transaksi jika belum ada agar query tidak menghasilkan error
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                balance_after REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            SELECT id, username, type, amount, balance_after, created_at 
            FROM transactions 
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        tx_list = [
            {
                "id": r[0],
                "username": r[1],
                "type": r[2],
                "amount": r[3],
                "balance_after": r[4],
                "created_at": r[5]
            } for r in rows
        ]
        return {"success": True, "transactions": tx_list}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat log transaksi: {str(e)}")
    finally:
        conn.close()

# ================= RUN SERVER DIRECTLY =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
