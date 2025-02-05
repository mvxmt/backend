from cryptography import fernet as fn
import pathlib

class CryptographyManager():
    fernet: fn.Fernet

    def __init__(self, machine_key: bytes) -> None:
        self.fernet = fn.Fernet(machine_key)

    
    def encrypt_bytes(self, f: bytes) -> bytes:
        return self.fernet.encrypt(f)
    

    def decrypt_bytes(self, f: bytes) -> bytes:
        return self.fernet.decrypt(f)
    

    def encrypt_file(self, f: pathlib.Path) -> bytes:
        if f.exists() and f.is_file():
            with open(f, "rb") as fp:
                return self.encrypt_bytes(fp.read())
            
    def decrypt_file(self, f: pathlib.Path) -> bytes:
        if f.exists() and f.is_file():
             with open(f, "rb") as fp:
                return self.decrypt_bytes(fp.read()) 