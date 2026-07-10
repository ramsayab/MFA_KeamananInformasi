# Panduan Instalasi & Pengujian Proyek Login MFA Aman (Aura Bank)

Dokumen ini berisi panduan lengkap untuk memasang (install), menjalankan, menguji, dan memahami pembagian tugas pembuatan sistem login aman menggunakan Multi-Factor Authentication (MFA) bertema **Bank Digital** berbasis **FastAPI** dan **SQLite**.

---

## 📂 Struktur Berkas Proyek

Proyek ini dirancang secara modular dan dibagi menjadi berkas-berkas berikut:
* 🏦 `main.py` - Berkas utama FastAPI (Router API, Inisialisasi Database SQLite `bank.db`, & Penyaji Frontend).
* 🔒 `auth_hash.py` - Modul Hashing Password (tugas **Anggota 1**).
* 🔑 `auth_otp.py` - Modul One-Time Password (tugas **Anggota 2**).
* 🎟️ `auth_session.py` - Modul Manajemen Sesi (tugas **Anggota 3**).
* 💳 `auth_role.py` - Modul Peran User & Transaksi Setor/Tarik (tugas **Anggota 4**).
* 🎨 `templates/index.html` - Halaman utama frontend (Desain premium bank digital dengan transisi antar card).

---

## 🛠️ Langkah Instalasi

### 1. Prasyarat (Prerequisites)
Pastikan komputer Anda sudah terpasang **Python 3.8** atau versi di atasnya.

### 2. Memasang Dependensi
Buka terminal (Command Prompt / PowerShell / Terminal VS Code) di folder proyek ini dan jalankan perintah berikut:
```bash
pip install -r requirements.txt
```
*Catatan: SQLite sudah merupakan pustaka bawaan (built-in) Python, sehingga tidak perlu diunduh secara terpisah.*

### 3. Menjalankan Aplikasi
Jalankan server lokal dengan perintah:
```bash
python main.py
```
Server akan menyala pada alamat: **`http://127.0.0.1:8000`**

Saat aplikasi pertama kali dijalankan, sistem akan otomatis membuat berkas database bernama `bank.db` di folder proyek ini.

---

## 👥 Panduan Tugas & Pembagian Kerja Kelompok

Setiap berkas keamanan saat ini diisi dengan implementasi sementara (mock/stub) agar aplikasi dapat langsung dijalankan untuk pengujian. Tugas masing-masing anggota adalah menggantinya dengan logika keamanan yang riil.

### 🔒 Anggota 1: Hashing Password (`auth_hash.py`)
* **Tujuan**: Mengganti mock hashing dengan algoritma hashing aman.
* **Rekomendasi**: Gunakan library `bcrypt`.
  ```bash
  pip install bcrypt
  ```
* **Tugas**:
  1. Lengkapi `hash_password(password: str) -> str`. Gunakan `bcrypt.hashpw` dan kembalikan string hash.
  2. Lengkapi `verify_password(plain_password: str, hashed_password: str) -> bool`. Gunakan `bcrypt.checkpw`.
  3. Perbarui daftar hash password awal pada database di berkas `main.py` pada dictionary `users_db` menggunakan hash bcrypt yang baru untuk user `budi` dan `admin`.

### 🔑 Anggota 2: Verifikasi OTP (`auth_otp.py`)
* **Tujuan**: Membuat kode OTP 6-digit dinamis yang aman dan menyimpannya di tabel database SQLite `otps`.
* **Rekomendasi**: Gunakan library bawaan Python `secrets` untuk membuat kode acak, atau pasang library `pyotp` untuk TOTP Google Authenticator.
* **Tugas**:
  1. Lengkapi `generate_otp(user_id: str) -> str`. Buat kode 6-digit acak, lalu simpan/update ke tabel `otps` di `bank.db` bersama waktu kedaluwarsa (`expires_at` = waktu sekarang + 120 detik).
  2. Lengkapi `verify_otp(user_id: str, otp_code: str) -> bool`. Ambil data dari tabel `otps` berdasarkan `user_id`, periksa apakah kode cocok dan belum melewati `expires_at`. Hapus kode dari database setelah berhasil diverifikasi (sekali pakai).

### 🎟️ Anggota 3: Manajemen Sesi (`auth_session.py`)
* **Tujuan**: Membuat token sesi kriptografis yang aman dan menyimpannya di tabel `sessions`.
* **Rekomendasi**: Gunakan JSON Web Token (`pyjwt`) atau Session ID acak berbasis UUID yang terdaftar di database server.
  ```bash
  pip install pyjwt
  ```
* **Tugas**:
  1. Lengkapi `create_session(user_id: str, role: str) -> str`. Buat token unik (misal: JWT yang ditandatangani SECRET_KEY) dan simpan ke tabel `sessions`.
  2. Lengkapi `verify_session(session_token: str) -> dict | None`. Dekode token JWT atau cari di tabel `sessions`. Jika valid dan belum kedaluwarsa, kembalikan dictionary `{"user_id": ..., "role": ...}`. Jika tidak valid/kedaluwarsa, kembalikan `None`.
  3. Lengkapi `destroy_session(session_token: str) -> bool`. Hapus baris sesi dari tabel `sessions` saat user menekan tombol Logout.

### 💳 Anggota 4: Role User & Transaksi (`auth_role.py`)
* **Tujuan**: Mengatur otorisasi akses berdasarkan peran (Role-Based Access Control) dan memproses transaksi Setor & Tarik Tunai langsung pada tabel database `balances`.
* **Tugas**:
  1. Lengkapi `check_role(user_role: str, required_role: str) -> bool`. Pastikan user memiliki role yang dibutuhkan (misal: customer).
  2. Lengkapi `process_deposit(user_id: str, amount: float) -> dict`. Tambahkan validasi agar input `amount` harus lebih besar dari 0. Update saldo di tabel `balances` menggunakan query:
     `UPDATE balances SET balance = balance + ? WHERE username = ?`
  3. Lengkapi `process_withdraw(user_id: str, amount: float) -> dict`. Pastikan jumlah penarikan > 0 dan sisa saldo setelah ditarik tidak kurang dari saldo minimum Rp 50.000,00. Jalankan query update saldo jika valid.
  4. (Opsional/Nilai Tambah): Buat tabel baru `transactions` di SQLite untuk mencatat riwayat mutasi setor/tarik secara permanen.

---

## 🧪 Skenario Pengujian Aplikasi

### Pengujian Akun Nasabah (Customer)
1. Buka browser dan arahkan ke `http://127.0.0.1:8000`.
2. Di halaman login, masukkan **Username**: `budi` dan **Password**: `budi123`. Klik **Masuk Aman**.
3. Di halaman OTP, perhatikan kotak indikator pengujian berwarna oranye yang menampilkan kode OTP aktif Anda (misalnya `123456`). Masukkan kode tersebut dan klik **Verifikasi & Masuk**.
4. Di Dashboard Customer, verifikasi bahwa:
   * Nama akun tertulis **budi**.
   * Role badge bertuliskan **CUSTOMER** (warna hijau).
   * Saldo awal adalah **Rp 500.000,00**.
5. Uji **Setor Tunai**: Masukkan nominal (misal Rp 100.000) atau klik tombol cepat **100K**, lalu klik **Konfirmasi Setoran**. Verifikasi saldo bertambah menjadi Rp 600.000,00 dan log transaksi mencatat setoran Anda.
6. Uji **Tarik Tunai**: Klik tab Tarik Tunai, masukkan nominal (misal Rp 150.000), dan klik **Konfirmasi Penarikan**. Verifikasi saldo berkurang menjadi Rp 450.000,00.
7. Klik **Logout** di pojok kanan atas, pastikan Anda kembali ke halaman Login.

### Pengujian Akun Pengawas (Admin)
1. Di halaman login, masukkan **Username**: `admin` dan **Password**: `admin123`. Klik **Masuk Aman**.
2. Masukkan kode OTP yang tertera dan verifikasi.
3. Di Dashboard Admin, verifikasi bahwa:
   * Nama akun tertulis **admin**.
   * Role badge bertuliskan **ADMIN** (warna indigo/ungu).
   * Kotak transaksi Setor & Tarik Tunai hilang dan digantikan oleh pesan peringatan: *"Akun Anda terdeteksi sebagai ADMINISTRATOR. Sesuai kepatuhan, transaksi keuangan diblokir bagi administrator."*
4. Ini membuktikan fitur otorisasi Role User (Anggota 4) berjalan dengan sukses!
5. Klik **Logout** untuk menyelesaikan pengujian.
