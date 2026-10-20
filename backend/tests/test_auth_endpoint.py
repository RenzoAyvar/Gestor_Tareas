"""Pruebas HTTP de integración sobre PostgreSQL real; CI levanta Postgres service."""
import asyncio
import os

os.environ.setdefault("JWT_SECRET", "integration-test-secret-not-for-deployment-123")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("DEV_CREATE_TABLES", "false")

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import delete

from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.user import Base, User

CORREO = "admin-test@practica.com"
PASSWORD = "admin123-test-only"

async def _setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.correo == CORREO))
        db.add(User(correo=CORREO, password_hash=hash_password(PASSWORD)))
        await db.commit()

async def _teardown():
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.correo == CORREO))
        await db.commit()
    await engine.dispose()

@pytest.fixture(scope="module", autouse=True)
def seed():
    asyncio.run(_setup())
    yield
    asyncio.run(_teardown())

@pytest.fixture
def client():
    with TestClient(app) as http:
        yield http

def test_login_200(client):
    response = client.post("/auth/login", json={"correo": CORREO.upper(), "password": PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["correo"] == CORREO
    assert body["token_type"] == "bearer"
    assert "password_hash" not in body
    decoded = jwt.decode(body["token"], os.environ["JWT_SECRET"], algorithms=["HS256"])
    assert decoded["sub"] == CORREO
    assert decoded["exp"] - decoded["iat"] == 3600

def test_login_401_password(client):
    response = client.post("/auth/login", json={"correo": CORREO, "password": "incorrecta"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Correo o contraseña incorrectos."}

def test_login_401_unknown_email(client):
    response = client.post("/auth/login", json={"correo": "nobody@example.com", "password": "incorrecta"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Correo o contraseña incorrectos."}

@pytest.mark.parametrize("body", [{"password": "abc"}, {"correo": CORREO},
                                   {"correo": "", "password": "abc"},
                                   {"correo": "x y@example.com", "password": "abc"},
                                   {"correo": " a@example.com", "password": "abc"}])
def test_login_422_missing_and_spaces(client, body):
    response = client.post("/auth/login", json=body)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
