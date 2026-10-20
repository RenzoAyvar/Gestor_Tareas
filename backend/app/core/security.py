import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(correo: str) -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET debe tener al menos 32 caracteres")
    minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    if minutes <= 0:
        raise RuntimeError("JWT_EXPIRE_MINUTES debe ser positivo")
    now = datetime.now(timezone.utc)
    payload = {"sub": correo, "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, secret, algorithm=ALGORITHM)
