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

import bcrypt

def hash_password(password: str) -> str:
    """
    Menghasilkan hash aman dari password mentah.
    
    Parameter:
    - password (str): Password mentah yang dimasukkan oleh pengguna.
    
    Mengembalikan:
    - str: Hasil hash password dalam bentuk string.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Memverifikasi apakah password mentah sesuai dengan hash yang disimpan.
    
    Parameter:
    - plain_password (str): Password mentah yang dimasukkan saat login.
    - hashed_password (str): Hash password yang tersimpan di database/sistem.
    
    Mengembalikan:
    - bool: True jika password cocok dengan hash, False jika tidak.
    """
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        return False
    if not hashed_password:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (TypeError, ValueError):
        return False
