import time
import sqlite3
import secrets
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_FILE = "bank.db"
OTP_VALIDITY_SECONDS = 120  # OTP valid selama 2 menit (120 detik)

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def send_otp_email(to_email: str, otp_code: str) -> bool:
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_str = os.environ.get("SMTP_PORT", "587")
    try:
        smtp_port = int(smtp_port_str)
    except ValueError:
        smtp_port = 587
        
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    # Deteksi jika kredensial belum diatur oleh pengguna
    if (not sender_email or not sender_password or 
        sender_email == "change_this@gmail.com" or 
        sender_password == "change_this_to_your_app_password"):
        print(f"\n[SMTP WARNING] Kredensial SMTP belum dikonfigurasi di file .env!")
        print(f"[SMTP WARNING] Email OTP tidak terkirim ke {to_email}.")
        print(f"[SMTP WARNING] Gunakan kode OTP ini untuk login pengujian: {otp_code}\n")
        return False
        
    # Mempersiapkan format email MIME
    msg = MIMEMultipart()
    msg['From'] = f"AURA BANK Security <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = f"[{otp_code}] Kode OTP Otorisasi Masuk AURA BANK"
    
    body = f"""Halo Nasabah AURA BANK,

Anda telah berhasil memasukkan kata sandi akun Anda. 
Gunakan kode OTP (One-Time Password) di bawah ini untuk menyelesaikan langkah verifikasi ganda (MFA) Anda:

👉 {otp_code} 👈

Kode di atas hanya berlaku selama 2 menit (120 detik) sejak email ini dikirim. 

Demi menjaga keamanan rekening dan data pribadi Anda:
- JANGAN membagikan kode OTP ini kepada siapa pun, termasuk pihak yang mengaku sebagai staf AURA BANK.
- Staff bank asli TIDAK AKAN PERNAH meminta kode OTP atau password Anda.

Jika Anda tidak merasa melakukan percobaan masuk, abaikan email ini dan segera ubah kata sandi rekening Anda.

Salam hangat,
AURA BANK Security Operations Center
"""
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Koneksi ke server SMTP Gmail menggunakan TLS aman
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"[SMTP] Sukses! Email OTP berhasil dikirim ke {to_email}")
        return True
    except Exception as e:
        print(f"[SMTP ERROR] Gagal mengirim email OTP ke {to_email}: {e}")
        print(f"[SMTP ERROR] Anda masih dapat melihat kode OTP ini di console/UI untuk pengujian: {otp_code}")
        return False

def generate_otp(user_id: str) -> str:
    otp_code = "".join(secrets.choice("0123456789") for _ in range(6))
    expires_at = time.time() + OTP_VALIDITY_SECONDS
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO otps (username, otp_code, expires_at) VALUES (?, ?, ?)",
            (user_id, otp_code, expires_at)
        )
        conn.commit()
        cursor.execute("SELECT email FROM users WHERE username = ?", (user_id,))
        row = cursor.fetchone()
        
        if row and row[0]:
            email_address = row[0]
            send_otp_email(email_address, otp_code)
        else:
            print(f"[WARNING] Pengguna {user_id} tidak memiliki alamat email terdaftar di database.")
            print(f"[WARNING] Kode OTP tetap dapat digunakan di console: {otp_code}")
            
    except sqlite3.Error as e:
        print(f"[DATABASE ERROR] Gagal memproses penyimpanan OTP ke database: {e}")
    finally:
        conn.close()
        
    return otp_code

def verify_otp(user_id: str, otp_code: str) -> bool:
    now = time.time()
    conn = _get_conn()
    is_valid = False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT otp_code, expires_at FROM otps WHERE username = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        
        if row:
            db_otp_code, expires_at = row
            if db_otp_code == otp_code and now <= expires_at:
                is_valid = True
                cursor.execute("DELETE FROM otps WHERE username = ?", (user_id,))
                conn.commit()
                print(f"[SECURITY] OTP untuk {user_id} berhasil diverifikasi dan dihapus (sekali pakai).")
            else:
                # Jika kedaluwarsa, hapus juga dari database untuk pembersihan
                if now > expires_at:
                    cursor.execute("DELETE FROM otps WHERE username = ?", (user_id,))
                    conn.commit()
                    print(f"[SECURITY] OTP untuk {user_id} kedaluwarsa dan telah dihapus.")
                else:
                    print(f"[SECURITY] Percobaan verifikasi OTP salah untuk {user_id}.")
        else:
            print(f"[SECURITY] Tidak ada kode OTP aktif yang ditemukan untuk {user_id}.")
            
    except sqlite3.Error as e:
        print(f"[DATABASE ERROR] Gagal melakukan verifikasi OTP dari database: {e}")
    finally:
        conn.close()
        
    return is_valid
