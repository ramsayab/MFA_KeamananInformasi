"""
TUGAS ANGGOTA 1: HASH PASSWORD
==============================
Petunjuk Pengerjaan:
1. Gantikan fungsi-fungsi di bawah ini dengan implementasi hashing password yang aman.
2. Sangat disarankan menggunakan library 'bcrypt'. Anda dapat menginstalnya dengan:
   pip install bcrypt
3. Pastikan tipe data input dan output sesuai dengan type hint yang telah ditentukan.
4. Fungsi verify_password harus mengembalikan nilai True jika password cocok, dan False jika tidak.
"""

def hash_password(password: str) -> str:
    """
    Menghasilkan hash aman dari password mentah.
    
    Parameter:
    - password (str): Password mentah yang dimasukkan oleh pengguna.
    
    Mengembalikan:
    - str: Hasil hash password dalam bentuk string.
    """
    # TODO: Anggota 1 harus mengganti kode di bawah ini dengan bcrypt hashing yang sesungguhnya.
    # Contoh implementasi bcrypt:
    # import bcrypt
    # salt = bcrypt.gensalt()
    # return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Mengembalikan string terbalik sebagai hash tiruan agar sistem bisa berjalan sebelum Anda menyelesaikannya.
    return f"mock_hash_{password[::-1]}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Memverifikasi apakah password mentah sesuai dengan hash yang disimpan.
    
    Parameter:
    - plain_password (str): Password mentah yang dimasukkan saat login.
    - hashed_password (str): Hash password yang tersimpan di database/sistem.
    
    Mengembalikan:
    - bool: True jika password cocok dengan hash, False jika tidak.
    """
    # TODO: Anggota 1 harus mengganti kode di bawah ini dengan verifikasi bcrypt yang sesungguhnya.
    # Contoh implementasi bcrypt:
    # import bcrypt
    # return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    # MOCK IMPLEMENTATION (Belum selesai / Sementara):
    # Memeriksa kesesuaian menggunakan metode mock yang sama dengan hash_password.
    return hashed_password == f"mock_hash_{plain_password[::-1]}"
