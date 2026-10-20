from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.schemas import LoginRequest, LoginResponse
from app.models.user import User

INVALID_CREDENTIALS = "Correo o contraseña incorrectos."
# Para comparación de bcrypt aun con usuario desconocido, reduciendo diferencias de tiempo.
_DUMMY_HASH = hash_password("dummy-password-for-timing-only")


async def authenticate(data: LoginRequest, db: AsyncSession) -> LoginResponse:
    correo = data.correo.strip().lower()
    result = await db.execute(select(User).where(User.correo == correo))
    user = result.scalar_one_or_none()

    matching = verify_password(data.password, user.password_hash if user else _DUMMY_HASH)
    if user is None or not matching:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)

    return LoginResponse(correo=correo, token=create_access_token(correo))
