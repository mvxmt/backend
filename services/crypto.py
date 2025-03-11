from cryptography import fernet as fn
import pathlib
import os
from contextlib import contextmanager
import tempfile
from config import Settings


class CryptographyManager:
    fernet: fn.Fernet

    def __init__(self, machine_keys: list[fn.Fernet]) -> None:
        assert type(machine_keys) is list
        assert type(machine_keys[0]) is fn.Fernet

        self.fernet = fn.MultiFernet(machine_keys)

    @staticmethod
    def from_settings(settings: Settings):
        return CryptographyManager([fn.Fernet(k) for k in settings.fernet_keys])

    def encrypt_bytes(self, f: bytes) -> bytes:
        return self.fernet.encrypt(f)

    def decrypt_bytes(self, f: bytes) -> bytes:
        return self.fernet.decrypt(f)

    def encrypt_string(self, s: str) -> str:
        assert type(s) is str
        return (self.encrypt_bytes(s.encode())).decode()

    def decrypt_string(self, s: str) -> str:
        assert type(s) is str
        return (self.decrypt_bytes(s.encode())).decode()

    def encrypt_file(self, f: pathlib.Path) -> bytes:
        if f.exists() and f.is_file():
            with open(f, "rb") as fp:
                return self.encrypt_bytes(fp.read())

    def decrypt_file(self, f: pathlib.Path) -> bytes:
        if f.exists() and f.is_file():
            with open(f, "rb") as fp:
                return self.decrypt_bytes(fp.read())

    @contextmanager
    def yield_decrypted_file(self, path: str | os.PathLike):
        "Given a file path that is encrypted, it will decrypt the file to a temporary location and when the context manager exits, delete the decrypted file"
        path = pathlib.Path(path)
        if path.exists() and path.is_file():
            by = self.decrypt_file(path)
            new_file, filename = tempfile.mkstemp()

            os.write(new_file, by)
            os.close(new_file)

            yield filename

            os.unlink(filename)
