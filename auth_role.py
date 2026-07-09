"""
TUGAS ANGGOTA 4: ROLE USER & TRANSAKSI (SETOR & TARIK) - VERSI STUB / BELUM SELESAI
=================================================================================
Petunjuk Pengerjaan:
1. Gantikan fungsi-fungsi di bawah ini dengan implementasi pemeriksaan hak akses (Role) 
   dan logika transaksi keuangan (Setor & Tarik Tunai) yang terhubung ke database SQLite.
2. Anda harus menghubungkan ke database SQLite "bank.db" untuk mengambil dan memperbarui saldo rekening nasabah.
3. Skema tabel 'balances' yang telah disediakan di database bank.db:
   - username (TEXT, Primary Key)
   - balance (REAL - nominal saldo)
4. Ketentuan Keamanan & Validasi Transaksi:
   - Otorisasi Peran: Gunakan fungsi `check_role` untuk memvalidasi bahwa hanya user dengan role 'customer' yang diperbolehkan melakukan setor atau tarik tunai.
   - Input Nominal: Pastikan nominal setor/tarik harus merupakan angka positif (> 0). Jika tidak valid, gagalkan transaksi.
   - Saldo Minimum: Penarikan saldo (Tarik Tunai) hanya boleh sukses jika saldo rekening setelah penarikan tidak kurang dari saldo minimum Rp 50.000,00.
5. Alur Setor Tunai (`process_deposit`):
   - Validasi input nominal setor (> 0).
   - Hubungkan ke SQLite "bank.db", ambil saldo saat ini dari tabel `balances` berdasarkan `user_id`.
   - Lakukan operasi penambahan: saldo baru = saldo lama + nominal setor.
   - Simpan saldo baru tersebut kembali ke database (UPDATE atau REPLACE).
   - Kembalikan dictionary hasil transaksi: `{"success": True, "message": "...", "new_balance": saldo_baru}`.
6. Alur Tarik Tunai (`process_withdraw`):
   - Validasi input nominal tarik (> 0).
   - Hubungkan ke SQLite "bank.db", ambil saldo saat ini dari tabel `balances` berdasarkan `user_id`.
   - Periksa apakah saldo setelah ditarik melanggar aturan saldo minimum (saldo_lama - nominal_tarik >= 50000).
   - Jika melanggar, gagalkan transaksi dengan mengembalikan: `{"success": False, "message": "...", "new_balance": saldo_lama}`.
   - Jika sukses, lakukan pengurangan saldo baru, simpan ke database, dan kembalikan sukses beserta nominal baru.
"""

# Saldo minimum yang harus tersisa di rekening setelah penarikan
MINIMUM_BALANCE = 50000.0

# Mocking saldo sederhana di memori hanya untuk testing awal frontend
mock_balances = {
    "budi": 500000.0,
    "admin": 0.0
}

def check_role(user_role: str, required_role: str) -> bool:
    """
    Memeriksa apakah role user memenuhi role yang dibutuhkan untuk mengakses fitur tertentu.
    
    Parameter:
    - user_role (str): Role milik pengguna saat ini (diperoleh dari data sesi).
    - required_role (str): Role minimal yang diperlukan untuk mengakses fitur.
    
    Mengembalikan:
    - bool: True jika role memenuhi syarat, False jika ditolak.
    """
    # TODO: Anggota 4 harus melengkapi logika pemeriksaan role secara aman.
    return user_role == required_role

def process_deposit(user_id: str, amount: float) -> dict:
    """
    Memproses penambahan saldo (setor tunai) langsung pada database SQLite.
    
    Parameter:
    - user_id (str): Username/ID user yang ingin menyetor uang.
    - amount (float): Jumlah uang yang akan disetor.
    
    Mengembalikan:
    - dict: Hasil transaksi, misalnya {"success": bool, "message": str, "new_balance": float}
    """
    # TODO: Anggota 4 harus menulis logika setor tunai yang aman ke tabel `balances` di SQLite.
    # Ingat untuk menambahkan validasi: nominal harus > 0.
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Mengupdate mock_balances lokal di memori agar dashboard frontend tetap update selama pengujian awal.
    if user_id not in mock_balances:
        mock_balances[user_id] = 0.0
    mock_balances[user_id] += amount
    return {
        "success": True,
        "message": f"Setor tunai berhasil sebesar Rp {amount:,.2f}",
        "new_balance": mock_balances[user_id]
    }

def process_withdraw(user_id: str, amount: float) -> dict:
    """
    Memproses pengurangan saldo (tarik tunai) langsung pada database SQLite.
    
    Parameter:
    - user_id (str): Username/ID user yang ingin menarik uang.
    - amount (float): Jumlah uang yang akan ditarik.
    
    Mengembalikan:
    - dict: Hasil transaksi, misalnya {"success": bool, "message": str, "new_balance": float}
    """
    # TODO: Anggota 4 harus menulis logika tarik tunai yang aman ke tabel `balances` di SQLite.
    # Ingat untuk menambahkan validasi: nominal > 0 dan saldo sisa tidak kurang dari MINIMUM_BALANCE (50.000).
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Validasi saldo minimum tiruan menggunakan mock_balances lokal.
    if user_id not in mock_balances:
        return {"success": False, "message": "User tidak ditemukan", "new_balance": 0.0}
        
    current_balance = mock_balances[user_id]
    if current_balance - amount < MINIMUM_BALANCE:
        return {
            "success": False,
            "message": f"Tarik tunai gagal. Saldo Anda tidak mencukupi untuk mempertahankan saldo minimum Rp {MINIMUM_BALANCE:,.2f}",
            "new_balance": current_balance
        }
        
    mock_balances[user_id] -= amount
    return {
        "success": True,
        "message": f"Tarik tunai berhasil sebesar Rp {amount:,.2f}",
        "new_balance": mock_balances[user_id]
    }

def get_balance(user_id: str) -> float:
    """
    Mendapatkan saldo saat ini untuk user tertentu dari database SQLite.
    """
    # TODO: Anggota 4 harus menulis logika pengambilan saldo dari database SQLite tabel `balances`.
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    return mock_balances.get(user_id, 0.0)
