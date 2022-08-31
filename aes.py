import pyaes
import hashlib
from base64 import b64decode, b64encode

class AES:
    def __init__(self, password) -> None:
        self.password = password
        self.hashed_password = bytes(hashlib.md5(bytes(password, encoding="utf-8")).hexdigest(), encoding="utf-8")

    @property
    def aes(self) -> pyaes.AESModeOfOperationCTR:
        return pyaes.AESModeOfOperationCTR(self.hashed_password)

    def encrypt(self, data: str) -> bytes:
        return self.aes.encrypt(data)

    def b64enc(self, data: str) -> str:
        return str(b64encode(self.encrypt(data)), encoding="utf-8")

    def decrypt(self, data: bytes) -> str:
        return str(self.aes.decrypt(data), encoding="utf-8")

    def b64dec(self, data: str) -> str:
        return self.decrypt(b64decode(data))
