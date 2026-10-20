"""Pruebas HTTP de integración sobre PostgreSQL real; CI levanta Postgres service."""
import asyncio
import os
from unittest.mock import AsyncMock

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
EXPECTED_INVALID_CREDENTIALS = {"detail": "Correo o contraseña incorrectos."}


def assert_no_sensitive_data(response):
    """El contrato nunca expone credenciales, hashes ni el secreto de firma."""
    response_text = response.text
    assert "password_hash" not in response_text
    assert PASSWORD not in response_text
    assert os.environ["JWT_SECRET"] not in response_text

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
    assert set(body) == {"correo", "token", "token_type"}
    assert body["correo"] == CORREO
    assert body["token_type"] == "bearer"
    assert jwt.get_unverified_header(body["token"])["alg"] == "HS256"
    decoded = jwt.decode(body["token"], os.environ["JWT_SECRET"], algorithms=["HS256"])
    assert decoded["sub"] == CORREO
    assert decoded["exp"] - decoded["iat"] == 3600
    assert_no_sensitive_data(response)

def test_login_401_password(client):
    response = client.post("/auth/login", json={"correo": CORREO, "password": "incorrecta"})
    assert response.status_code == 401
    assert response.json() == EXPECTED_INVALID_CREDENTIALS
    assert_no_sensitive_data(response)

def test_login_401_unknown_email(client):
    response = client.post("/auth/login", json={"correo": "nobody@example.com", "password": "incorrecta"})
    assert response.status_code == 401
    assert response.json() == EXPECTED_INVALID_CREDENTIALS
    assert_no_sensitive_data(response)

@pytest.mark.parametrize(
    ("body", "invalid_field"),
    [
        ({"password": "abc"}, "correo"),
        ({"correo": CORREO}, "password"),
        ({"correo": "", "password": "abc"}, "correo"),
        ({"correo": CORREO, "password": ""}, "password"),
        ({"correo": "x y@example.com", "password": "abc"}, "correo"),
        ({"correo": "\ta@example.com", "password": "abc"}, "correo"),
        ({"correo": "a@example.com\n", "password": "abc"}, "correo"),
    ],
)
def test_login_422_missing_and_spaces(client, monkeypatch, body, invalid_field):
    authenticate = AsyncMock()
    monkeypatch.setattr("app.api.auth.authenticate", authenticate)

    response = client.post("/auth/login", json=body)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any(error["loc"] == ["body", invalid_field] for error in detail)
    authenticate.assert_not_awaited()
    assert_no_sensitive_data(response)
