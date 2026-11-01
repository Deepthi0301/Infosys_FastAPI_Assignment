
import os
import uuid

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pwdlib import PasswordHash
from jose import jwt, JWTError


# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing. Add it to your .env file.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
password_hash = PasswordHash.recommended()


# Hash password
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# Generate JWT access token
def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })

    encoded_token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_token


# Verify JWT access token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except JWTError:
        return None
