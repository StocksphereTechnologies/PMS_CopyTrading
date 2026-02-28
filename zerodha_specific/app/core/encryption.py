"""
Encryption utilities for sensitive credentials
Uses Fernet symmetric encryption with SHA256-derived key
"""
from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting/decrypting sensitive data"""

    def __init__(self):
        """Initialize encryption service with secret key"""
        key = self._derive_key(settings.SECRET_KEY)
        self.cipher = Fernet(key)

    @staticmethod
    def _derive_key(secret: str) -> bytes:
        """Derive a Fernet key from secret string using SHA256"""
        key = hashlib.sha256(secret.encode()).digest()
        return base64.urlsafe_b64encode(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string, returns base64-encoded ciphertext"""
        if not plaintext:
            return ""
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string, returns plaintext"""
        if not ciphertext:
            return ""
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise


encryption_service = EncryptionService()
