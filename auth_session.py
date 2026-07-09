"""
TUGAS ANGGOTA 3: MANAJEMEN SESI (Session Management) - VERSI STUB / BELUM SELESAI
================================================================================
Petunjuk Pengerjaan:
1. Gantikan fungsi-fungsi di bawah ini dengan implementasi manajemen sesi yang aman menggunakan database SQLite.
2. Anda harus menghubungkan ke database SQLite "bank.db" untuk mendaftarkan dan memverifikasi token sesi.
3. Skema tabel 'sessions' yang telah disediakan di database bank.db:
   - session_token (TEXT, Primary Key)
   - username (TEXT)
   - role (TEXT)
   - expires_at (REAL - epoch timestamp dari time.time())
4. Alur Pembuatan Sesi (`create_session`):
   - Buat token unik (misalnya UUID menggunakan library bawaan `uuid`, atau gunakan token JWT yang ditandatangani).
   - Simpan data sesi (token, username, role, expires_at) ke tabel `sessions` di `bank.db`.
   - Kembalikan token sesi dalam tipe data `str`.
5. Alur Verifikasi Sesi (`verify_session`):
   - Query data sesi dari tabel `sessions` berdasarkan `session_token`.
   - Jika sesi ditemukan dan belum melewati waktu kedaluwarsa (`expires_at`), kembalikan dictionary data sesi: `{"user_id": username, "role": role}`.
   - Jika tidak ditemukan atau telah kedaluwarsa, hapus data kedaluwarsa tersebut dari database, lalu kembalikan `None`.
6. Alur Penghapusan Sesi (`destroy_session`):
   - Hapus (DELETE) data sesi dari tabel `sessions` berdasarkan `session_token`.
   - Kembalikan `True` jika berhasil dihapus, atau `False` jika tidak ditemukan.
"""
import time

def create_session(user_id: str, role: str) -> str:
    """
    Membuat sesi baru di database SQLite setelah user berhasil melewati login ganda.
    
    Parameter:
    - user_id (str): Username/ID dari user yang login.
    - role (str): Role milik user (misal: 'customer' atau 'admin').
    
    Mengembalikan:
    - str: Token sesi yang dihasilkan untuk dikirim ke client.
    """
    # TODO: Anggota 3 harus menulis logika pembuatan token sesi dan menyimpannya ke tabel `sessions` di SQLite.
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Mengembalikan token statis tiruan agar sistem bisa berjalan untuk pengetesan.
    return "mock_session_token_123"

def verify_session(session_token: str) -> dict | None:
    """
    Memverifikasi apakah token sesi terdaftar di database SQLite dan belum kedaluwarsa.
    
    Parameter:
    - session_token (str): Token sesi dari client (Bearer token).
    
    Mengembalikan:
    - dict | None: Dictionary berisi {"user_id": ..., "role": ...} jika valid,
                   atau None jika token tidak valid/kedaluwarsa.
    """
    # TODO: Anggota 3 harus menulis logika verifikasi sesi dari database SQLite.
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Menyimulasikan verifikasi token statis.
    # Jika token cocok dengan mock token, kembalikan data sesi tiruan.
    if session_token == "mock_session_token_123":
        return {
            "user_id": "budi",
            "role": "customer"
        }
    elif session_token == "mock_session_token_admin":
        return {
            "user_id": "admin",
            "role": "admin"
        }
    return None

def destroy_session(session_token: str) -> bool:
    """
    Menghapus sesi dari database SQLite ketika user logout.
    
    Parameter:
    - session_token (str): Token sesi yang ingin dihapus.
    
    Mengembalikan:
    - bool: True jika berhasil dihapus, False jika tidak.
    """
    # TODO: Anggota 3 harus menulis logika penghapusan baris sesi dari database SQLite.
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Selalu mengembalikan True untuk simulasi logout sukses.
    return True
