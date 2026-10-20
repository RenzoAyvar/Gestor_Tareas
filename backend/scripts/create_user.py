"""Alta explícita del usuario local: python -m scripts.create_user --correo admin@practica.com"""
import argparse
import asyncio
from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models.user import User

async def create(correo: str, password: str):
    async with SessionLocal() as db:
        exists = await db.scalar(select(User).where(User.correo == correo))
        if exists:
            raise SystemExit("Ya existe un usuario con ese correo.")
        db.add(User(correo=correo, password_hash=hash_password(password)))
        await db.commit()
    await engine.dispose()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--correo", required=True)
    args = p.parse_args()
    correo = args.correo.strip().lower()
    if not correo or any(c.isspace() for c in correo):
        p.error("Correo inválido")
    password = getpass("Contraseña del nuevo usuario (no visible): ")
    if len(password) < 8:
        p.error("Usa una contraseña de al menos 8 caracteres")
    asyncio.run(create(correo, password))
    print("Usuario creado. No se ha almacenado contraseña en texto plano.")
