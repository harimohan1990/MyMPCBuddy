import pytest
from app.core.security import (
    encrypt_token,
    decrypt_token,
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)


def test_password_hashing():
    pw = "SecretPassw0rd!"
    hashed = get_password_hash(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_jwt_token_cycle():
    user_id = "user-12345"
    token = create_access_token(user_id)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_aes_gcm_token_encryption():
    raw_oauth_token = "ya29.a0AfH6SMB_secret_google_oauth_token_123456789"
    cipher_text = encrypt_token(raw_oauth_token)
    assert cipher_text != raw_oauth_token
    decrypted = decrypt_token(cipher_text)
    assert decrypted == raw_oauth_token


def test_empty_token_encryption():
    assert encrypt_token("") == ""
    assert decrypt_token("") == ""
