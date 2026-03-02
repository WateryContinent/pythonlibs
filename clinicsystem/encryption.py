from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64


# --- Key derivation from password ---
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


# --- Encrypt ---
def encrypt(plaintext: str, password: str) -> str:
    salt = os.urandom(16)
    key = derive_key(password, salt)

    iv = os.urandom(16)
    cipher = Cipher(
        algorithms.AES(key),
        modes.CFB(iv),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

    return base64.b64encode(salt + iv + ciphertext).decode()


# --- Decrypt ---
def decrypt(encoded_ciphertext: str, password: str) -> str:
    data = base64.b64decode(encoded_ciphertext)

    salt = data[:16]
    iv = data[16:32]
    ciphertext = data[32:]

    key = derive_key(password, salt)

    cipher = Cipher(
        algorithms.AES(key),
        modes.CFB(iv),
        backend=default_backend()
    )

    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext.decode()


# ✅ ONLY runs if this file itself is executed
if __name__ == "__main__":

    while True:
        choice = input(
            "Type 'encrypt' to encrypt or 'decrypt' to decrypt (or 'quit'): "
        ).lower()

        if choice == "encrypt":
            text = input("Enter text: ")
            password = input("Password: ")
            print("\nEncrypted:\n", encrypt(text, password), "\n")

        elif choice == "decrypt":
            encrypted_text = input("Encrypted text: ")
            password = input("Password: ")
            try:
                print("\nDecrypted:\n",
                      decrypt(encrypted_text, password), "\n")
            except Exception:
                print("Decryption failed.")

        elif choice == "quit":
            break