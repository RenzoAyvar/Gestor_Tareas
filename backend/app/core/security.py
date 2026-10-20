import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (TypeError, ValueError):
        return False


def create_access_token(correo: str) -> str:
    secret = _jwt_secret()

    try:
        minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    except ValueError as exc:
        raise RuntimeError("JWT_EXPIRE_MINUTES debe ser un entero positivo") from exc
    if minutes <= 0:
        raise RuntimeError("JWT_EXPIRE_MINUTES debe ser positivo")

    now = datetime.now(timezone.utc)
    payload = {"sub": correo, "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Return the token subject, or ``None`` for any invalid credential."""
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[ALGORITHM])
    except (JWTError, RuntimeError, TypeError, ValueError):
        return None

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        return None
    return subject


def _jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET debe tener al menos 32 caracteres")
    return secret
