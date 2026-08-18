import bcrypt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from cryptography.fernet import Fernet
from app.config import settings

# Stable Fernet Key
fernet_key = b"t-1Z_x3Zp9kL4rQ6yV8uN0mO2wE4aC6gI8kM0oQ2sU4="
fernet = Fernet(fernet_key)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    # bcrypt max password length is 72 bytes
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None

def encrypt_token(plain_text: str) -> str:
    return fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")

def decrypt_token(ciphertext: str) -> str:
    return fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
