import pytest
from app.services.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    encrypt_token,
    decrypt_token
)

def test_password_hashing():
    pwd = "SuperSecret123!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPwd123", hashed) is False

def test_jwt_token_encode_decode():
    data = {"sub": "user_123", "email": "user@example.com"}
    token = create_access_token(data)
    assert token is not None
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_123"
    assert decoded["email"] == "user@example.com"

def test_fernet_token_encryption_decryption():
    raw = "linkedin_oauth_access_token_ABC123456"
    encrypted = encrypt_token(raw)
    assert encrypted != raw
    assert not encrypted.startswith("linkedin_")
    decrypted = decrypt_token(encrypted)
    assert decrypted == raw
