"""
TUGAS ANGGOTA 2: VERIFIKASI OTP (One-Time Password) - VERSI STUB / BELUM SELESAI
==============================================================================
Petunjuk Pengerjaan:
1. Gantikan fungsi-fungsi di bawah ini dengan implementasi pembuatan dan verifikasi OTP yang aman menggunakan database SQLite.
2. Anda harus menghubungkan ke database SQLite "bank.db" untuk menyimpan kode OTP dinamis.
3. Skema tabel 'otps' yang telah disediakan di database bank.db:
   - username (TEXT, Primary Key)
   - otp_code (TEXT)
   - expires_at (REAL - epoch timestamp dari time.time())
4. Alur Pembuatan OTP (`generate_otp`):
   - Buat kode OTP acak 6-digit (misalnya menggunakan library bawaan Python `secrets`).
   - Simpan atau timpa (INSERT OR REPLACE) kode OTP tersebut ke tabel `otps` di database `bank.db` bersama waktu kedaluwarsa (misalnya valid selama 120 detik / 2 menit).
   - Kembalikan kode OTP tersebut dalam tipe data `str`.
5. Alur Verifikasi OTP (`verify_otp`):
   - Ambil data OTP dari tabel `otps` berdasarkan `user_id`/username.
   - Periksa apakah kode OTP cocok dan belum melewati waktu kedaluwarsa (`expires_at`).
   - Jika valid, hapus data OTP tersebut dari database (karena OTP hanya boleh sekali pakai / one-time use), lalu kembalikan `True`.
   - Jika tidak valid atau kedaluwarsa, kembalikan `False`.
"""
import time

def generate_otp(user_id: str) -> str:
    """
    Membuat kode OTP 6-digit untuk user dan menyimpannya ke database SQLite.
    
    Parameter:
    - user_id (str): ID unik/username dari user yang sedang melakukan login.
    
    Mengembalikan:
    - str: Kode OTP 6-digit yang dihasilkan. Harus tipe data str (misal: "123456").
    """
    # TODO: Anggota 2 harus menulis logika pembuatan OTP dinamis yang aman dan menyimpannya ke database SQLite.
    # Hubungkan ke SQLite dengan `import sqlite3`, buka koneksi ke "bank.db", jalankan query INSERT/REPLACE ke tabel `otps`.
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Mengembalikan kode statis "123456" agar sistem tetap bisa berjalan untuk pengujian awal frontend.
    return "123456"

def verify_otp(user_id: str, otp_code: str) -> bool:
    """
    Memverifikasi apakah kode OTP yang dimasukkan valid dan belum kedaluwarsa berdasarkan database SQLite.
    
    Parameter:
    - user_id (str): ID unik/username dari user.
    - otp_code (str): Kode OTP yang diinputkan oleh user pada frontend.
    
    Mengembalikan:
    - bool: True jika OTP valid dan belum kedaluwarsa, False jika tidak.
    """
    # TODO: Anggota 2 harus menulis logika verifikasi OTP dengan mencocokkan input dengan data di tabel `otps`,
    # melakukan pengecekan kedaluwarsa waktu (timestamp), dan menghapus baris OTP tersebut setelah sukses digunakan.
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Hanya mencocokkan string statis "123456" untuk mempermudah pengetesan awal.
    return otp_code == "123456"
