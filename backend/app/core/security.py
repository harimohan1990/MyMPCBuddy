import os
import base64
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import bcrypt
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


# ==========================================
# AES-256-GCM Provider Token Encryption
# ==========================================

def _get_encryption_key() -> bytes:
    """Returns 32 bytes key for AES-256-GCM."""
    raw = settings.ENCRYPTION_KEY
    try:
        decoded = base64.b64decode(raw)
        if len(decoded) == 32:
            return decoded
    except Exception:
        pass
    # Fallback to key padded/hashed to 32 bytes
    import hashlib
    return hashlib.sha256(raw.encode('utf-8')).digest()


def encrypt_token(plain_token: str) -> str:
    """
    Encrypts sensitive OAuth tokens using AES-256-GCM.
    Returns: base64-encoded string containing [12-byte Nonce + Ciphertext + Tag]
    """
    if not plain_token:
        return ""
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # Standard 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, plain_token.encode('utf-8'), None)
    payload = nonce + ciphertext
    return base64.b64encode(payload).decode('utf-8')


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypts AES-256-GCM encrypted token.
    """
    if not encrypted_token:
        return ""
    try:
        raw = base64.b64decode(encrypted_token.encode('utf-8'))
        nonce = raw[:12]
        ciphertext = raw[12:]
        key = _get_encryption_key()
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decrypt OAuth token: {str(e)}")
