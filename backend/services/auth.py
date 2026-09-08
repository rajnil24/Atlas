import os
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt


JWT_ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")

ACCESS_TOKEN_EXPIRE_MINUTES = 15

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password is too long")

    salt = bcrypt.gensalt()

    password_hash = bcrypt.hashpw(
        password_bytes,
        salt,
    )

    return password_hash.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hash_bytes,
    )


def create_access_token(user_id: int) -> str:

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token


def decode_access_token(token: str) -> dict:

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

    return payload